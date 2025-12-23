import logging
import os
import sys

def init_logger(config: dict):
    """
    Configures the root logger based on the provided dictionary.
    """
    log_file = config.get("file")
    log_level_str = config.get("level", "INFO").upper()
    log_format = config.get("format", "%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except OSError as e:
                print(f"Failed to create log directory: {e}")
        
        try:
            handlers.append(logging.FileHandler(log_file, mode='w'))
        except OSError as e:
            print(f"Failed to create log file handler: {e}")

    logging.basicConfig(
        level=getattr(logging, log_level_str, logging.INFO),
        format=log_format,
        handlers=handlers,
        force=True
    )
    
    logging.info("Logger initialized.")