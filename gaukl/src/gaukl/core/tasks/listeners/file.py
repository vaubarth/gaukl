import glob
import logging
import time
from pathlib import Path

from gaukl.core.context.context import Context
from gaukl.core.tasks.listener import listener, on_request
from gaukl.core.helper.files import read_path

logger = logging.getLogger('file_listener')


@on_request()
def handle_files(context: Context, file_path: Path) -> Context:
    logger.info(f'checking {file_path}')
    time.sleep(0.5)

    stat_info = file_path.stat()
    context.parsed_request_header()['gaukl_file_path'] = str(file_path)
    context.parsed_request_header()['gaukl_file_size'] = stat_info.st_size
    context.parsed_request_header()['gaukl_file_mtime'] = stat_info.st_mtime
    context.parsed_request_header()['gaukl_file_ctime'] = stat_info.st_ctime
    context.parsed_request_header()['gaukl_file_name'] = str(file_path.name)
    context['request']['body']['raw'] = file_path.read_text()

    return context


@listener(shortname='file_listener')
def listener(context: Context, infile_scheme: str = None, outfile_path: str = None, sleep_time: int = 10) -> None:
    outfile_path = Path(outfile_path)
    while True:
        in_files = glob.glob(infile_scheme)

        if len(in_files) == 0:
            logger.debug('no files')
        else:
            for file_path in in_files:
                context = handle_files(context, Path(file_path), outfile_path)
                with outfile_path.joinpath(context.parsed_response_header()['gaukl_file_name']).open('w+') as f:
                    f.write(context['response']['body']['raw'])
            logger.debug(f'sleeping {sleep_time}')
        time.sleep(sleep_time)
