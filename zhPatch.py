# Website: http://zhpatch.evemodx.com/
# QQ Group Number: 494245573

import localization
import localization.const
import localization.localizationBase
import logmodule

def patch_localization():
    
    def _ReadLocalizationLanguagePickles_decorator(func):
        def wrapper(self, prefix, supportedLanguages, dataType):
            ret = func(self, prefix, supportedLanguages, dataType)
            self._LoadLanguagePickle(prefix, 'zh', dataType)
            return ret
        return wrapper

    def GetByMessageID_decorator(func):
        def wrapper(self, messageID, languageID=None, **kwargs):
            ret = func(self, messageID, languageID='zh', **kwargs)
            if not ret or ret.startswith('[no '):
                ret = func(self, messageID, languageID=languageID, **kwargs)
            return ret
        return wrapper

    localization.localizationBase.Localization._ReadLocalizationLanguagePickles = _ReadLocalizationLanguagePickles_decorator(localization.localizationBase.Localization._ReadLocalizationLanguagePickles)
    localization.localizationBase.Localization.GetByMessageID = GetByMessageID_decorator(localization.localizationBase.Localization.GetByMessageID)

    localization._ReadLocalizationLanguagePickles = localization.LOCALIZATION_REF._ReadLocalizationLanguagePickles
    localization.GetByMessageID = localization.LOCALIZATION_REF.GetByMessageID


patch_localization()

__import__('autoexec_client')
