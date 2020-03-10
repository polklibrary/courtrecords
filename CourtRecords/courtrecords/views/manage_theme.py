
from courtrecords.security.acl import ACL
from courtrecords.models import Users, Config
from courtrecords.utilities.validators import Validators
from courtrecords.views import BaseView
from courtrecords.views.emailer import Emailer
from pyramid.httpexceptions import HTTPFound
from pyramid.url import route_url
from pyramid.view import view_config
from pyramid.response import FileResponse

from zipfile import ZipFile
import os, datetime, math, io


class ManageTheme(BaseView):


    ALLOWED_FILES = ('.pt','.png','.jpg','.gif','.jpeg','.js','.css','.txt','.TXT','.eot','.svg','.ttf','.woff','.md','.ico')
    sizeused = ''

    @view_config(route_name='manage_theme', renderer='../themes/templates/admin/theme.pt', permission=ACL.EDITOR)
    def manage_theme(self):
        self.sizeused = '' #reset
        
        # Priority calls
        if 'theme.upload' in self.request.params:
            self.theme_upload() 
        if 'theme.package' in self.request.params:
            self.theme_compress() 
        if 'theme.delete' in self.request.params:
            self.theme_delete()
        
        # set zips
        self.set('zips', self.list_zips())
            
        # set download, will clear any set zips above
        if 'theme.download' in self.request.params:
            self.theme_download()
        
        return self.response
        
        
    def theme_download(self):
        path = self.request.params.get('theme.package.selected', '')
        if os.path.exists(path):       
            self.response = FileResponse(path)
            self.response.headers['Content-Type'] = 'application/download'
            self.response.headers['Accept-Ranges'] = 'bite'
            self.response.headers['Content-Disposition'] = 'attachment;filename=' + str(os.path.basename(path))
            return self.response
            

    def theme_delete(self):
        path = self.request.params.get('theme.package.selected', '')
        if os.path.exists(path):
            os.remove(path)


    def list_zips(self):
        zippaths = []
        totalsize = 0
        path = self.settings('theme_directory', '')
        for folderName, subfolders, filenames in os.walk(path):
            for filename in filenames:
                filePath = os.path.join(folderName, filename)
                if filePath.endswith('.zip'):
                    size = os.path.getsize(filePath)
                    totalsize += size
                    zippaths.append({
                        'path': filePath,
                        'name': filename,
                        'size': self.friendly_byte_size(size)
                    })
        self.sizeused = self.friendly_byte_size(totalsize)
        return zippaths
        
        
    def theme_compress(self):
        datestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
        themepath = self.settings('theme_directory', '')
        themefolder = os.path.basename(themepath)
        zipFileName = os.path.join(themepath, datestamp + "-theme.zip")
        if os.path.exists(themepath):
            with ZipFile(zipFileName, 'w') as zipObj:
                # Iterate over all the files in directory
                for folderName, subfolders, filenames in os.walk(themepath):
                    for filename in filenames:
                        # create complete filepath of file in directory
                        filePath = os.path.join(folderName, filename)
                        # Add file to zip
                        if not filePath.endswith('.zip'):
                            zipObj.write(filePath, filePath.replace(themepath, themefolder))


    def friendly_byte_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])
        
    def theme_upload(self):
        themezip = self.request.params.get('theme.upload.file')
        themepath = self.settings('theme_directory', '')
        with ZipFile(themezip.file, 'r') as zipObj:
            for file in zipObj.namelist():
                if file.startswith('themes/') and not file.startswith('themes/themes/') and file.endswith(self.ALLOWED_FILES):
                    zipObj.extract(file, os.path.join(themepath, '..'))

        
    # def theme_upload(self):
        # themezip = self.request.params.get('theme.upload.file')
        # themepath = self.settings('theme_directory', '')
        # with ZipFile(themezip.file, 'r') as zipObj:
            # zipObj.extractall(os.path.join(themepath, '..'))

        