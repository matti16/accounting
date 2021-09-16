class PatchedSpooledTempfile(object): 
    def __init__(self, obj):
        self._wrapped_obj = obj

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self._wrapped_obj, attr)

    @property                                                                                                                          
    def readable(self):                                                                                                                
        return self._file.readable                                                                                                     

    @property                                                                                                                          
    def writable(self):                                                                                                                
        return self._file.writable                                                                                                     

    @property                                                                                                                          
    def seekable(self):                                                                                                                
        return self._file.seekable 