import ftplib
import zipfile
from os import remove, makedirs
from os.path import join, isdir
from time import sleep


class FtpCollector:
    def __init__(self, host, host_folder='', username='anonymous', passwd='anonymous', dest_folder=None):
        self.host = host
        self.host_folder = host_folder
        self.username = username
        self.passwd = passwd
        self.dest_folder = dest_folder
        self.ftp = ftplib.FTP(host, username, passwd)

    def set_username(self, username):
        self.username = username

    def set_password(self, password):
        self.password = password

    def set_dest_folder(self, dest_folder):
        self.dest_folder = dest_folder

    def __collect(self, file_list):
        for filename in file_list:
            print 'Collecting {}...'.format(filename)
            dest_file = join(self.dest_folder, filename)
            fp = open(dest_file, 'wb')
            self.ftp.retrbinary('RETR ' + filename, fp.write)
            fp.close()

    def collect_files(self, file_list):
        self.ftp.login()
        self.ftp.cwd(self.host_folder)
        try:
            self.__collect(file_list)
        finally:
            self.ftp.close()

    def collect_all_files(self):
        self.ftp.login()

        self.ftp.cwd(self.host_folder)
        all_files = self.ftp.nlst()
        try:
            self.__collect(all_files)
        finally:
            self.ftp.close()

        return all_files

    def unpack(self, file_list, rm_zips=False):
        for f in file_list:
            filename = f[:-4]  # cut off the .zip extension
            try:
                zf = zipfile.ZipFile(join(self.dest_folder, f))
                # It's taking a while for the file to be accessible after download.
                # If the file is not found (KeyError) wait a bit and try again.
                for i in xrange(3):
                    try:
                        zf.extractall(path=join(self.dest_folder, filename))
                        break
                    except KeyError:
                        sleep(3)

                print '{} unpacked successfully'.format(f)
            except zipfile.BadZipfile:
                print '{} was not unpacked successfully'.format(f)
            finally:
                zf.close()
            if rm_zips:
                remove(join(self.dest_folder, f))

    def collect_and_unpack(self, file_list, rm_zips=False):
        self.collect_files(file_list)
        self.unpack(file_list, rm_zips=rm_zips)

    def collect_all_and_unpack(self, rm_zips=False):
        file_list = self.collect_all_files()
        self.unpack(file_list, rm_zips=rm_zips)


def main():
    dest_folder = join('..', 'StateTracts')
    if not isdir(dest_folder):
        makedirs(dest_folder)

    files = ['tl_2017_01_tract.zip', 'tl_2017_02_tract.zip']

    f = FtpCollector(host='ftp.census.gov', host_folder='/geo/tiger/TIGER2017/BG', dest_folder=dest_folder)

    f.collect_all_and_unpack(rm_zips=True)


if __name__ == '__main__':
    main()
