import argparse
from datetime import datetime
import logging
import sys
import traceback

from emt_qc.emt_block_duration.emt_block_duration import emt_block_qc_run_all


class Args(argparse.Namespace):

    def __init__(self):
        super().__init__()
        # Arguments that could be passed in through the command line
        self.reprocess = False
        self.debug = False

        self.__parse()


    def __parse(self):
        p = argparse.ArgumentParser(prog='EMT_Block_Duration_QC',
                                    description='Generates a .csv and .txt file with the length of each experiment block '
                                                'for all PIPELINE_8 folders on the isilon')
        p.add_argument('--reprocess', action='store_true',
                       help='Re-run QC on all PIPELINE_8 folders', 
                       default=False, required=False)
        p.add_argument('--debug', action='store_true', 
                       help='Enable debug mode', 
                       default=False, required=False)
        
###############################################################################

def configure_logging(debug: bool):
    f = logging.Formatter(fmt='[%(asctime)s][%(levelname)s] %(message)s')
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(f)
    fileHandler = logging.FileHandler(filename=f"fov_qc_cli_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.log", mode="w")
    fileHandler.setFormatter(f)
    log = logging.getLogger() # root logger
    log.handlers = [streamHandler, fileHandler] # overwrite handlers
    log.setLevel(logging.DEBUG if debug else logging.INFO)
        
def main():
    args = Args()
    debug = args.debug
    configure_logging(debug)
    log = logging.getLogger(__name__)

    try:
        log.info("Start EMT_Block_Duration_QC")
        log.info(f"Reprocess = {args.reprocess}")
        log.info(args)

        emt_block_qc_run_all(reprocess=args.reprocess)

    except Exception as e:
        log.error("=============================================")
        log.error("\n\n" + traceback.format_exc())
        log.error("=============================================")
        log.error("\n\n" + str(e) + "\n")
        log.error("=============================================")
        sys.exit(1)


###############################################################################
# Allow caller to directly run this module (usually in development scenarios)

if __name__ == '__main__':
    main()