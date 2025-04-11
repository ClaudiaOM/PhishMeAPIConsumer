import os
import logging
from time import sleep
import uuid
import csv
import io

from cofense_api_consumer.consumer import APIConsumer
from cofense_api_consumer.custom_exceptions import RateLimitError
from cofense_api_consumer.params_builder import ParamBuilder
from database.repository import BaseRepository
from database.repository.settings_repository import SettingsRepository
from database.models import Base, Company, Scenario, Timeline, ScenarioData, Settings
from sqlalchemy.exc import IntegrityError
from database.database_context import Database


def setup_logging():
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
    # Set working directory to script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    logger = setup_logging()

    try:
        cofense_run(logger)
    except Exception as e:
        logger.error(f"An exception occurred in main(): {e}", exc_info=True)


def cofense_run(logger):
    try:
        logger.info("Starting the Cofense run process.")

        database = Database(
            username='',
            password='',
            host='Claudia',
            port=1433,
            database='Cofense',
            driver='ODBC Driver 17 for SQL Server'
        )

        logger.info("Database Loaded")
        session = database.session

        # Load additional settings
        settings_repository = SettingsRepository(session)
        base_url = settings_repository.get_cofense_api_url()
        last_run = settings_repository.get_last_run()
        logger.info("Settings Loaded")

        if base_url is None or last_run is None:
            logger.error("No settings configured for ApiUrl or Last Run Date")
            raise ValueError("No settings configured for ApiUrl or Last Run Date")


        all_companies = get_companies(session, logger)

        all_companies.sort(key=lambda x: x.Name)

        for company in all_companies:
            logger.info(f"=============================================================")
            logger.info(f"Processing company: {company.Name}")

            try:
                # Create API consumer instance for a company
                api = APIConsumer(base_url, company.API)

                scenarios = company_scenarios(api, company.Id, session, last_run, logger)

                for sc in scenarios:
                    logger.info(f"Downloading scenario: {sc.Title} for company: {company.Name}")
                    try:
                        if sc.Status != 'Scheduled' and not sc.Fully_Downloaded:
                            logger.info(f"Downloading timeline data for scenario: {sc.Title}")
                            scenario_timeline(api, sc.Id, session, sc.Activity_Timeline_Url, logger)
                            logger.info(f"Downloading full data for scenario: {sc.Title}")
                            scenario_fulldata(api, sc.Id, session, sc.Full_CSV_Url, logger)
                            logger.info("Scenario data download completed.")
                            sc.Fully_Downloaded = True
                            update_scenario(sc, session, logger)
                    except Exception as ex:
                        logger.error(f"Error downloading scenario data for {sc.Title} in {company.Name}: {ex}", exc_info=True)

            except Exception as ex:
                logger.error(f"Error processing company {company.Name}: {ex}", exc_info=True)

            logger.info(f"=============================================================")
            logger.info("\n\n")
        logger.info("Company processing completed.")

    except Exception as e:
        logger.error(f"Error in cofense_run(): {e}", exc_info=True)
    finally:
        session.close()
        logger.info("Cofense run process completed.")


def get_companies(session, logger):
    try:
        repository = BaseRepository(session, Company)
        companies = repository.get()
        logger.info(f"Retrieved {len(companies)} companies from database.")
        return companies
    except Exception as e:
        logger.error(f"Error retrieving companies: {e}", exc_info=True)
        raise


def company_scenarios(company_api, company_id, session, date, logger):
    try:
        endpoint = "scenarios"
        repository = BaseRepository(session, Scenario)
        builder = ParamBuilder()
        params = builder.started_after(date).build()

        try:
            scenarios = company_api.get(endpoint, params)
        except Exception as e:
            logger.error(f"Error retrieving scenarios for company ID {company_id}: {e}", exc_info=True)
            raise
        

        logger.info(f"Retrieved {len(scenarios)} scenarios for company ID {company_id}.")

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
                yield entity
            except Exception as e:
                logger.error(f"Error processing scenario {sc.get('Title', 'Unknown')}: {e}", exc_info=True)
    except Exception as e:        
        logger.error(f"Error retrieving scenarios for company ID {company_id}: {e}", exc_info=True)
        raise


def update_scenario(scenario, session, logger):
    try:
        repository = BaseRepository(session, Scenario)
        repository.save_entity(scenario)
        logger.info(f"Updated scenario {scenario.Title}")
    except Exception as e:
        logger.error(f"Error updating scenario {scenario.Title}: {e}", exc_info=True)


def scenario_timeline(company_api, scenario_id, session, timeline_url, logger):
    try:
        repository = BaseRepository(session, Timeline)

        try:
            timeline = company_api.get_csv_url(timeline_url) 
        except RateLimitError as e:
            wait_time = e.wait_time
            logger.warning(f"API Token Busy while downloading timeline data. Waiting {wait_time} seconds.")
            sleep(wait_time)
            timeline = company_api.get_csv_url(timeline_url)

        # Remove lines starting with '#' and any empty lines        
        data = "\n".join(
            [line for line in timeline.split("\n") if not line.startswith("#") and line.strip()]
        )

        # Read CSV data into a list of dictionaries
        reader = csv.DictReader(io.StringIO(data))
        data_collection = list(reader)
        logger.info(f"Processing {len(data_collection)} timeline entries for scenario ID {scenario_id}.")

        for item in data_collection:
            try:
                entity = Timeline.from_json(item)
                if entity.In_User_Agents_Charts and entity.Action != 'Email Webbug Tracked':
                    entity.Scenario_Id = scenario_id
                    entity.Id = uuid.uuid4()
                    repository.save_entity(entity)
                    logger.info(f"Inserted Scenario timeline for {entity.Recipient} with scenario id {scenario_id}.")
            except IntegrityError:
                session.rollback()
                logger.warning(f"Failed to insert Timeline with ID {entity.Id} due to IntegrityError.")
            except Exception as e:
                logger.error(f"Error processing timeline entry: {e}", exc_info=True)
    except Exception as e:       
        logger.error(f"Error retrieving timeline for scenario ID {scenario_id}: {e}", exc_info=True)
        raise


def scenario_fulldata(company_api, scenario_id, session, full_csv_url, logger):
    try:
        repository = BaseRepository(session, ScenarioData)
        try:
            full_data = company_api.get_csv_url(full_csv_url)
        except RateLimitError as e:
            wait_time = e.wait_time
            logger.warning(f"API Token Busy while downloading full data. Waiting {wait_time} seconds.")
            sleep(wait_time)
            full_data = company_api.get_csv_url(full_csv_url)
            
        # Read CSV data into a list of dictionaries
        reader = csv.DictReader(io.StringIO(full_data))
        data_collection = list(reader)
        count = len(data_collection)
        logger.info(f"Processing {count} full data entries for scenario ID {scenario_id}.")

        for item in data_collection:
            try:
                entity = ScenarioData.from_json(item)
                entity.Scenario_Id = scenario_id
                entity.Id = uuid.uuid4()
                repository.save_entity(entity)
                logger.info(f"Inserted ScenarioData for {entity.Recipient_Name} for {scenario_id}.")
            except IntegrityError:
                session.rollback()
                logger.warning(f"Failed to insert ScenarioData with ID {entity.Id} due to IntegrityError.")
            except Exception as e:
                logger.error(f"Error processing full data entry: {e}", exc_info=True)

        sleep_time = (count / 1000) + 2
        logger.info(f"Sleeping for {sleep_time} seconds to throttle API usage.")
        sleep(sleep_time)
    except Exception as e:
        logger.error(f"Error retrieving full data for scenario ID {scenario_id}: {e}", exc_info=True)
        raise


# --- Script Entry Point ---
if __name__ == "__main__":
    main()