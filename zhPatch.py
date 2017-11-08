# Version: 20171108
# Website: https://zhpatch.evemodx.com/
# QQ Group Number: 494245573

import localization
import localization.internalUtil
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
            ret = None
            if not languageID or languageID != 'en-us' or localization.internalUtil.GetLanguageID() == 'en-us':
                ret = func(self, messageID, languageID='zh', **kwargs)
            if not ret or ret.startswith('[no '):
                ret = func(self, messageID, languageID='en-us', **kwargs)
            return ret
        return wrapper

    localization.localizationBase.Localization._ReadLocalizationLanguagePickles = _ReadLocalizationLanguagePickles_decorator(localization.localizationBase.Localization._ReadLocalizationLanguagePickles)
    localization.localizationBase.Localization.GetByMessageID = GetByMessageID_decorator(localization.localizationBase.Localization.GetByMessageID)

    localization._ReadLocalizationLanguagePickles = localization.LOCALIZATION_REF._ReadLocalizationLanguagePickles
    localization.GetByMessageID = localization.LOCALIZATION_REF.GetByMessageID

def patch_zhtext():

    def load_text():
        import requests
        try:
            headers = {
                'User-Agent': 'requests/zhpatch'
            }
            data = requests.get(r'https://nosni.lodestone.zhpatch.evemodx.com/api/all', headers=headers).json()
            if data['status'] != 200:
                raise Exception('Patch error', 'API server not responding correct data')
                return None
            return data['data']
        except:
            return None

    def _LoadPickleData_decorator(func):
        def wrapper(self, pickleName, dataType):
            ret = func(self, pickleName, dataType)
            if 'zh' in pickleName:
                zhtext_revised = load_text()
                if zhtext_revised:
	                for messageID, text_revised in zhtext_revised.items():
	                    ret[1][int(messageID)] = (text_revised, None, None)
            return ret
        return wrapper

    localization.localizationBase.Localization._LoadPickleData = _LoadPickleData_decorator(localization.localizationBase.Localization._LoadPickleData)

def patch_font():
    from carbonui import languageConst, fontconst
    try:
        fontconst.FONTFAMILY_PER_WINDOWS_LANGUAGEID[languageConst.LANG_JAPANESE] = fontconst.FONTFAMILY_PER_WINDOWS_LANGUAGEID[languageConst.LANG_CHINESE]
    except:
        pass

patch_zhtext()
patch_localization()
patch_font()

__import__('autoexec_client')
