# -*- coding: UTF-8 -*-
import glob
import os
from datetime import datetime
import shutil
import requests
from myhelpers.cdr import parse_cdr
from myhelpers.logging import logger

filefolder = '/opt/cdrfiles'
savefolder = '/opt/cdrfiles_archives'

def files_move(file):
    filename = str(os.path.basename(file))
    print(filename)
    year = datetime.now().strftime("%Y")
    month = datetime.now().strftime("%m")
    date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    if not os.path.exists(savefolder):
        os.mkdir(savefolder)
    savefolderd = savefolder + '/' + year + '/'
    if not os.path.exists(savefolderd):
        os.mkdir(savefolderd)
    savefolderd = savefolder + '/'+ year + '/' + month + '/'
    if not os.path.exists(savefolderd):
        os.mkdir(savefolderd)
    shutil.move(file, savefolderd + date + '_' + filename)  # to move files from
    logger.info(file + ' moved')

def csv_files_read(filefolder):
    logger.info(filefolder)
    for f in glob.glob(filefolder + "**"
                       + os.environ.get('FTP_3CX_FILEEXT'),
                       recursive=False):
        logger.info(f)
        csv = open(f, 'r')
        count = 0
        while True:
            count += 1
            # Get next line from file
            line = csv.readline()
            # if line is empty
            # end of file is reached
            if not line:
                break
            testline = line.split(',')
            if testline[0].startswith('Call'):
                cdrs, cdrdetails = parse_cdr(line)
                logger.info('cdr: ', cdrs)
                logger.info('cdrdetails: ', cdrdetails)
                webapi_url_cdr = os.environ.get('API_URL') + '/api/v1/cdr'
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                r_cdr = requests.post(webapi_url_cdr,data=cdrs, headers=headers)
                logger.info(r_cdr.status_code)
                logger.info(r_cdr.content)

                print(r_cdr.status_code, r_cdr.content)

                webapi_url_cdr_details = os.environ.get('API_URL') + '/api/v1/cdrdetails'
                r_cdrdetails = requests.post(webapi_url_cdr_details, data=cdrdetails, headers=headers)
                logger.info(r_cdrdetails.status_code)
                logger.info(r_cdrdetails.content)
                print(r_cdrdetails.status_code, r_cdrdetails.content)

            logger.info("Line{}: {}".format(count, line.strip()))
        csv.close()
        files_move(f)


