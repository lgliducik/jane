
import logging

logging.basicConfig(filename='log.log', filemode='w', level=logging.INFO, format="%(asctime)s %(name)s:%(levelname)s: %(message)s")
sqlalchemy_logger = logging.getLogger('sqlalchemy.engine.base.Engine')
sqlalchemy_logger.setLevel(logging.WARNING)