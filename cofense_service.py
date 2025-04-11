import os
import logging
from time import sleep
import uuid
import csv
import io
from datetime import datetime, timedelta

from cofense_api_consumer.consumer import APIConsumer
from cofense_api_consumer.custom_exceptions import RateLimitError
from cofense_api_consumer.params_builder import ParamBuilder
from database.repository import BaseRepository
from database.repository.settings_repository import SettingsRepository
from database.models import Base, Company, Scenario, Timeline, ScenarioData, Settings
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from database.database_context import Database


class CofenseService:
    def __init__(self, logger=None, config=None):
        """Initialize the Cofense Service with logger and configuration."""
        self.logger = logger or self._setup_logging()
        self.config = config or {}
        self.rate_limit_tracker = {}  # Track rate limits by company
        
        # Connect to database
        self.database = Database(
            username=self.config.get('username', ''),
            password=self.config.get('password', ''),
            host=self.config.get('host', 'Claudia'),
            port=self.config.get('port', 1433),
            database=self.config.get('database', 'Cofense'),
            driver=self.config.get('driver', 'ODBC Driver 17 for SQL Server')
        )
        
        self.session = self.database.session
        self.settings_repository = SettingsRepository(self.session)
        
        # Load settings
        self.base_url = self.settings_repository.get_cofense_api_url()
        self.last_run = self.settings_repository.get_last_run()
        
        if self.base_url is None or self.last_run is None:
            self.logger.error("No settings configured for ApiUrl or Last Run Date")
            raise ValueError("No settings configured for ApiUrl or Last Run Date")

    def _setup_logging(self):
        """Set up logging for the service."""
        logger = logging.getLogger('CofenseService')
        logger.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')

        # File Handler
        log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CofenseService.log')
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Optional: Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def run(self):
        """Main entry point to run the Cofense service."""
        try:
            self.logger.info("Starting the Cofense run process.")
            
            all_companies = self.get_companies()
            all_companies.sort(key=lambda x: x.Name)

            for company in all_companies:
                self.process_company(company)
                
            # Update last run time
            current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            self.settings_repository.update_last_run(current_time)
            self.logger.info(f"Updated last run time to {current_time}")
                
        except Exception as e:
            self.logger.error(f"Error in run(): {e}", exc_info=True)
        finally:
            self.session.close()
            self.logger.info("Cofense run process completed.")

    def get_companies(self):
        """Retrieve all companies from the database."""
        try:
            repository = BaseRepository(self.session, Company)
            companies = repository.get()
            self.logger.info(f"Retrieved {len(companies)} companies from database.")
            return companies
        except Exception as e:
            self.logger.error(f"Error retrieving companies: {e}", exc_info=True)
            raise

    def process_company(self, company):
        """Process scenarios for a single company."""
        correlation_id = str(uuid.uuid4())
        self.logger.info(f"[{correlation_id}] =============================================================")
        self.logger.info(f"[{correlation_id}] Processing company: {company.Name}")

        try:
            # Create API consumer instance for a company
            api = APIConsumer(self.base_url, company.API)

            # Check if company is rate limited
            if company.Name in self.rate_limit_tracker:
                wait_until = self.rate_limit_tracker[company.Name]
                current_time = datetime.now()
                
                if current_time < wait_until:
                    wait_seconds = (wait_until - current_time).total_seconds()
                    self.logger.info(f"[{correlation_id}] Company {company.Name} is rate limited. Waiting {wait_seconds:.1f} seconds.")
                    sleep(wait_seconds)
                    
                # Reset rate limit after waiting
                self.rate_limit_tracker.pop(company.Name, None)

            scenarios = self.company_scenarios(api, company.Id, correlation_id)

            for sc in scenarios:
                self.process_scenario(api, company, sc, correlation_id)

        except Exception as ex:
            self.logger.error(f"[{correlation_id}] Error processing company {company.Name}: {ex}", exc_info=True)

        self.logger.info(f"[{correlation_id}] =============================================================")
        self.logger.info("\n\n")

    def process_scenario(self, api, company, scenario, correlation_id):
        """Process a single scenario, downloading its data."""
        self.logger.info(f"[{correlation_id}] Processing scenario: {scenario.Title} for company: {company.Name}")
        
        try:
            if scenario.Status != 'Scheduled' and not scenario.Fully_Downloaded:
                # Download timeline data
                if scenario.Activity_Timeline_Url:
                    self.logger.info(f"[{correlation_id}] Downloading timeline data for scenario: {scenario.Title}")
                    self.scenario_timeline(api, scenario.Id, scenario.Activity_Timeline_Url, correlation_id, company)
                
                # Download full scenario data
                if scenario.Full_CSV_Url:
                    self.logger.info(f"[{correlation_id}] Downloading full data for scenario: {scenario.Title}")
                    self.scenario_fulldata(api, scenario.Id, scenario.Full_CSV_Url, correlation_id, company)
                
                # Mark scenario as fully downloaded
                self.logger.info(f"[{correlation_id}] Scenario data download completed.")
                scenario.Fully_Downloaded = True
                self.update_scenario(scenario, correlation_id)
                
        except RateLimitError as e:
            # Set rate limit for this company
            wait_time = e.wait_time + 60  # Add a buffer minute
            until = datetime.now() + timedelta(seconds=wait_time)
            self.rate_limit_tracker[company.Name] = until
            self.logger.warning(f"[{correlation_id}] Rate limit hit for company {company.Name}. Setting cooldown until {until}")
            
        except Exception as ex:
            self.logger.error(f"[{correlation_id}] Error downloading scenario data for {scenario.Title} in {company.Name}: {ex}", exc_info=True)

    def company_scenarios(self, company_api, company_id, correlation_id):
        """Retrieve and process scenarios for a company."""
        try:
            endpoint = "scenarios"
            repository = BaseRepository(self.session, Scenario)
            builder = ParamBuilder()
            params = builder.started_after(self.last_run).build()

            try:
                scenarios = company_api.get(endpoint, params)
            except Exception as e:
                self.logger.error(f"[{correlation_id}] Error retrieving scenarios for company ID {company_id}: {e}", exc_info=True)
                raise
            
            self.logger.info(f"[{correlation_id}] Retrieved {len(scenarios)} scenarios for company ID {company_id}.")

            result_scenarios = []
            for sc in scenarios:
                try:
                    entity = Scenario.from_json(sc)
                    existing_entity = repository.get_entity(entity.Id)
                    entity.Company_Id = company_id
                    if existing_entity is not None:
                        entity.Fully_Downloaded = existing_entity.Fully_Downloaded
                    else:
                        entity.Fully_Downloaded = False
                    repository.save_entity(entity)
                    result_scenarios.append(entity)
                except Exception as e:
                    self.logger.error(f"[{correlation_id}] Error processing scenario {sc.get('Title', 'Unknown')}: {e}", exc_info=True)
            
            return result_scenarios
            
        except Exception as e:        
            self.logger.error(f"[{correlation_id}] Error retrieving scenarios for company ID {company_id}: {e}", exc_info=True)
            raise

    def update_scenario(self, scenario, correlation_id):
        """Update a scenario in the database."""
        try:
            repository = BaseRepository(self.session, Scenario)
            repository.save_entity(scenario)
            self.logger.info(f"[{correlation_id}] Updated scenario {scenario.Title}")
        except Exception as e:
            self.logger.error(f"[{correlation_id}] Error updating scenario {scenario.Title}: {e}", exc_info=True)

    def scenario_timeline(self, company_api, scenario_id, timeline_url, correlation_id, company):
        """Download and process timeline data for a scenario."""
        try:
            repository = BaseRepository(self.session, Timeline)

            try:
                timeline = self._get_with_rate_limit_handling(
                    company_api.get_csv_url, 
                    timeline_url,
                    company,
                    correlation_id
                )
            except Exception as e:
                if isinstance(e, RateLimitError):
                    raise  # Let the calling method handle the rate limit
                self.logger.error(f"[{correlation_id}] Error downloading timeline: {e}", exc_info=True)
                return

            # Remove lines starting with '#' and any empty lines        
            data = "\n".join(
                [line for line in timeline.split("\n") if not line.startswith("#") and line.strip()]
            )

            # Read CSV data into a list of dictionaries
            reader = csv.DictReader(io.StringIO(data))
            data_collection = list(reader)
            self.logger.info(f"[{correlation_id}] Processing {len(data_collection)} timeline entries for scenario ID {scenario_id}.")

            # Get existing timeline entries for this scenario to avoid duplicates
            existing_entries = {}
            for timeline_entry in self.session.query(Timeline).filter(Timeline.Scenario_Id == scenario_id).all():
                key = f"{timeline_entry.Recipient}_{timeline_entry.Action}_{timeline_entry.Timestamp}"
                existing_entries[key] = timeline_entry

            inserted_count = 0
            skipped_count = 0
            
            for item in data_collection:
                try:
                    entity = Timeline.from_json(item)
                    if entity.In_User_Agents_Charts and entity.Action != 'Email Webbug Tracked':
                        entity.Scenario_Id = scenario_id
                        
                        # Create a unique key for deduplication
                        entry_key = f"{entity.Recipient}_{entity.Action}_{entity.Timestamp}"
                        
                        if entry_key in existing_entries:
                            skipped_count += 1
                            continue  # Skip this entry, it's a duplicate
                            
                        entity.Id = uuid.uuid4()
                        repository.save_entity(entity)
                        inserted_count += 1
                        
                        # Add to existing entries to prevent duplicates in current batch
                        existing_entries[entry_key] = entity
                        
                except IntegrityError:
                    self.session.rollback()
                    skipped_count += 1
                    self.logger.warning(f"[{correlation_id}] Failed to insert Timeline due to IntegrityError.")
                except Exception as e:
                    self.logger.error(f"[{correlation_id}] Error processing timeline entry: {e}", exc_info=True)
            
            self.logger.info(f"[{correlation_id}] Timeline processing complete. Inserted: {inserted_count}, Skipped: {skipped_count}")
            
        except Exception as e:       
            self.logger.error(f"[{correlation_id}] Error retrieving timeline for scenario ID {scenario_id}: {e}", exc_info=True)
            if isinstance(e, RateLimitError):
                raise  # Let the calling method handle the rate limit
            
    def scenario_fulldata(self, company_api, scenario_id, full_csv_url, correlation_id, company):
        """Download and process full scenario data."""
        try:
            repository = BaseRepository(self.session, ScenarioData)
            
            try:
                full_data = self._get_with_rate_limit_handling(
                    company_api.get_csv_url, 
                    full_csv_url,
                    company,
                    correlation_id
                )
            except Exception as e:
                if isinstance(e, RateLimitError):
                    raise  # Let the calling method handle the rate limit
                self.logger.error(f"[{correlation_id}] Error downloading full data: {e}", exc_info=True)
                return
                
            # Read CSV data into a list of dictionaries
            reader = csv.DictReader(io.StringIO(full_data))
            data_collection = list(reader)
            count = len(data_collection)
            self.logger.info(f"[{correlation_id}] Processing {count} full data entries for scenario ID {scenario_id}.")

            # Get existing timeline entries for this scenario to avoid duplicates
            existing_entries = {}
            for data_entry in self.session.query(ScenarioData).filter(ScenarioData.Scenario_Id == scenario_id).all():
                key = f"{data_entry.Email}_{data_entry.Last_Email_Status_Timestamp}"
                existing_entries[key] = data_entry

            batch_size = 100  # Process in batches
            inserted_count = 0
            skipped_count = 0
            entities_batch = []
            
            for item in data_collection:
                try:
                    entity = ScenarioData.from_json(item)
                    entity.Scenario_Id = scenario_id
                    
                    # Create a unique key for deduplication
                    entry_key = f"{entity.Email}_{entity.Last_Email_Status_Timestamp}"

                    # Skip if we already have data for this email in this scenario
                    if entry_key in existing_entries:
                        skipped_count += 1
                        continue
                        
                    entity.Id = uuid.uuid4()
                    entities_batch.append(entity)
                    
                    # Add to existing set to prevent duplicates in current batch
                    existing_entries[entry_key] = entity  
                    
                    # Process batch if it reaches the batch size
                    if len(entities_batch) >= batch_size:
                        self._save_batch(repository, entities_batch, correlation_id)
                        inserted_count += len(entities_batch)
                        entities_batch = []
                        
                except Exception as e:
                    self.logger.error(f"[{correlation_id}] Error processing full data entry: {e}", exc_info=True)

            # Save any remaining entities
            if entities_batch:
                self._save_batch(repository, entities_batch, correlation_id)
                inserted_count += len(entities_batch)
            
            self.logger.info(f"[{correlation_id}] Full data processing complete. Inserted: {inserted_count}, Skipped: {skipped_count}")

            # Throttle API usage to prevent overloading
            sleep_time = max(2, count / 1000)  # At least 2 seconds, or more for larger datasets
            self.logger.info(f"[{correlation_id}] Throttling: sleeping for {sleep_time:.1f} seconds")
            sleep(sleep_time)
            
        except Exception as e:
            self.logger.error(f"[{correlation_id}] Error retrieving full data for scenario ID {scenario_id}: {e}", exc_info=True)
            if isinstance(e, RateLimitError):
                raise  # Let the calling method handle the rate limit

    def _save_batch(self, repository, entities, correlation_id):
        """Save a batch of entities, handling transaction issues."""
        try:
            for entity in entities:
                repository.save_entity(entity)
            self.logger.info(f"[{correlation_id}] Saved batch of {len(entities)} entities")
        except IntegrityError:
            self.session.rollback()
            # Fall back to one-by-one insertion to skip problematic records
            successful = 0
            for entity in entities:
                try:
                    repository.save_entity(entity)
                    successful += 1
                except IntegrityError:
                    self.session.rollback()
                except Exception as e:
                    self.session.rollback()
                    self.logger.error(f"[{correlation_id}] Error saving entity: {e}", exc_info=True)
            self.logger.info(f"[{correlation_id}] Saved {successful}/{len(entities)} entities after rollback")
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"[{correlation_id}] Batch save error: {e}", exc_info=True)

    def _get_with_rate_limit_handling(self, api_function, url, company, correlation_id, max_retries=3):
        """Call API function with rate limit handling."""
        retry_count = 0
        while retry_count < max_retries:
            try:
                return api_function(url)
            except RateLimitError as e:
                retry_count += 1
                wait_time = e.wait_time
                
                if retry_count >= max_retries:
                    # Set rate limit for this company and propagate the exception
                    until = datetime.now() + timedelta(seconds=wait_time + 60)  # Add a buffer minute
                    self.rate_limit_tracker[company.Name] = until
                    self.logger.warning(f"[{correlation_id}] Rate limit maximum retries exceeded. Company {company.Name} rate limited until {until}")
                    raise
                
                self.logger.warning(f"[{correlation_id}] API Token Busy for {company.Name}. Retry {retry_count}/{max_retries} after {wait_time} seconds.")
                sleep(wait_time)


def setup_logging():
    """Set up logging for the main script."""
    logger = logging.getLogger('CofenseService')
    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')

    # File Handler
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CofenseService.log')
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Optional: Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def main():
    """Main entry point for the script."""
    # Set working directory to script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    logger = setup_logging()

    try:
        # Configuration could be loaded from environment variables or config file
        config = {
            'username': '',
            'password': '',
            'host': 'Claudia',
            'port': 1433,
            'database': 'Cofense',
            'driver': 'ODBC Driver 17 for SQL Server'
        }
        
        service = CofenseService(logger=logger, config=config)
        service.run()
    except Exception as e:
        logger.error(f"An exception occurred in main(): {e}", exc_info=True)


# --- Script Entry Point ---
if __name__ == "__main__":
    main()