# 20220308
import __builtin__
import os.path
import blue
import uthread
from eveprefs import boot
import localization
import localization.internalUtil
import localization.localizationBase

def _ReadLocalizationLanguagePickles_decorator(func):
    def wrapper(self, prefix, supportedLanguages, dataType):
        ret = func(self, prefix, supportedLanguages, dataType)
        ext_pickle_path = os.path.join(blue.remoteFileCache.cacheFolder, '..', 'localization_fsd_zh.pickle')
        if os.path.exists(ext_pickle_path):
            try:
                import whitelistpickle, eveLocalization
                unPickledObject = whitelistpickle.load(open(ext_pickle_path, 'rb'))
                eveLocalization.LoadMessageData(*unPickledObject)
            except:
                pass
        else:
            self._LoadLanguagePickle(prefix, 'zh', dataType)
        
        try:
            import eve.client.script.ui.util.searchUtil
            if eve.client.script.ui.util.searchUtil.GetResultsList.__name__ == 'GetResultsList':
                eve.client.script.ui.util.searchUtil.GetResultsList = GetResultsList_decorator(eve.client.script.ui.util.searchUtil.GetResultsList)
        except:
            pass
        return ret
    return wrapper

def Get_decorator(func):
    def wrapper(self, messageIDorLabel, languageID=None, **kwargs):
        ret = None
        if not languageID or (languageID not in ('en-us', 'en') or localization.internalUtil.GetLanguageID() == 'en-us'):
            ret = func(self, messageIDorLabel, languageID='zh', **kwargs)
        if not ret or ret.startswith('[no messageid:'):
            ret = func(self, messageIDorLabel, languageID='en-us', **kwargs)
        return ret
    return wrapper

def GetResultsList_decorator(func):
    import evetypes
    from inventoryrestrictions import is_contractable
    from eve.client.script.ui.util.searchUtil import _FormatSearchInput
    from eve.common.script.search.const import ResultType
    from textImporting.textToTypeIDFinder import TextToTypeIDFinder, SEARCH_LOCALIZED
    published_type_ids = [type_id for type_id in evetypes.Iterate() if evetypes.IsPublished(type_id) and is_contractable(type_id)]
    type_id_finder = TextToTypeIDFinder(published_type_ids, True)
    def wrapper(searchStr, groupIDList, *args, **kwargs):
        ret = func(searchStr, groupIDList, *args, **kwargs)
        if groupIDList == [ResultType.item_type]:
            cleaned_search_str = _FormatSearchInput(searchStr).lower()
            result = type_id_finder.FindTypeIDsWithPartialMatch(cleaned_search_str, SEARCH_LOCALIZED)
            return list(set(ret).union(result))
        return ret
    return wrapper  

def patch_font():
    from carbonui import languageConst, fontconst
    try:
        fontconst.FONTFAMILY_PER_WINDOWS_LANGUAGEID[languageConst.LANG_JAPANESE] = fontconst.FONTFAMILY_PER_WINDOWS_LANGUAGEID[languageConst.LANG_ENGLISH]
        fontconst.FONTFAMILY_PER_WINDOWS_LANGUAGEID[languageConst.LANG_KOREAN] = fontconst.FONTFAMILY_PER_WINDOWS_LANGUAGEID[languageConst.LANG_CHINESE]
    except:
        pass

def reload_modules():
    reload_modules = (
        "eve.client.script.ui.shared.mapView.mapViewColorHandler",
        "eve.client.script.ui.shared.mapView.filters.mapFilterActualColor",
        "eve.client.script.ui.shared.mapView.filters.mapFilterEDENCOMFortress",
        "eve.client.script.ui.shared.mapView.filters.mapFilterEDENCOMMinorVictories",
        "eve.client.script.ui.shared.mapView.filters.mapFilterTriglavianMinorVictories",
        "eve.client.script.ui.shared.mapView.filters.filtersByID",
        "eve.client.script.ui.shared.mapView.mapViewSettings",
        "eve.client.script.ui.shared.mapView.controls.mapViewCheckboxOptionButton"
    )
    import sys
    for module in reload_modules:
        if module in sys.modules:
            try:
                reload(sys.modules[module])
            except:
                pass

def patch():
    localization.localizationBase.Localization._ReadLocalizationLanguagePickles = _ReadLocalizationLanguagePickles_decorator(localization.localizationBase.Localization._ReadLocalizationLanguagePickles)
    localization.localizationBase.Localization.Get = Get_decorator(localization.localizationBase.Localization.Get)
    localization._ReadLocalizationLanguagePickles = localization.LOCALIZATION_REF._ReadLocalizationLanguagePickles
    localization.Get = localization.LOCALIZATION_REF.Get
    patch_font()
    localization.LoadLanguageData()
    reload_modules()
    if hasattr(__builtin__, 'cfg'):
        cfg.ReloadLocalizedNames()
    if hasattr(__builtin__, 'sm') and sm.state == 4:
        sm.ChainEvent('ProcessUIRefresh')
        sm.ScatterEvent('OnUIRefresh')

if boot.region != 'optic' and localization.Get.__name__ == 'Get':
    uthread.new(patch)
