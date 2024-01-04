import os

from django.core.files.uploadedfile import UploadedFile
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from img_compression import compress_img


class ImageUploadHandler(TemporaryFileUploadHandler):
    pass
    # def file_complete(self, file_size):
    # 	print(f'1, {self.file_name}')
    # 	fn = compress_img(self.file.temporary_file_path())
    # 	print(f'fn: {fn}')
    # 	print(f'temp_path {self.file.temporary_file_path()}')
    # 	self.file = UploadedFile(
    #           fn, os.path.basename(fn), self.content_type, 0, self.charset, self.content_type_extra
    #       )
    # 	print(f'the nmew filename is {self.file.name}')
    # 	self.file_name = self.file.name
    # 	#self.file.seek(0)
    # 	self.file.size = os.path.getsize(fn)
    # 	print(f'2, {self.file}')
    # 	return self.file
