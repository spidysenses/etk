from typing import List
from enum import Enum, auto
import datetime, re, calendar, pytz
from tzlocal import get_localzone
from dateutil.relativedelta import relativedelta

from etk.etk import ETK
from etk.extractor import Extractor, InputType
from etk.extractors.spacy_rule_extractor import SpacyRuleExtractor
from etk.etk_extraction import Extraction
from etk.dependencies.date_extractor_resources.constants import units, singleton_regex, \
    spacy_rules, directions, num_to_digit, spanish_to_english, language_date_order

# to avoid typo:
EXTRACT_FIRST_DATE_ONLY = 'extract_first_date_only'
ADDITIONAL_FORMATS = 'additional_formats'
USE_DEFAULT_FORMATS = 'use_default_formats'
IGNORE_DATES_BEFORE = 'ignore_dates_before'
IGNORE_DATES_AFTER = 'ignore_dates_after'
DETECT_RELATIVE_DATES = 'detect_relative_dates'
RELATIVE_BASE = 'relative_base'
PREFERRED_DATE_ORDER = 'preferred_date_order'
PREFER_LANGUAGE_DATE_ORDER = 'prefer_language_date_order'
TIMEZONE = 'timezone'
TO_TIMEZONE = 'to_timezone'
RETURN_AS_TIMEZONE_AWARE = 'return_as_timezone_aware'
PREFER_DAY_OF_MONTH = 'prefer_day_of_month'
PREFER_DATES_FROM = 'prefer_dates_from'


class DateResolution(Enum):
    """
    date resolution when convert a datetime object to iso format string
    """
    SECOND = auto()
    MINUTE = auto()
    HOUR = auto()
    DAY = auto()
    MONTH = auto()
    YEAR = auto()


class DateExtractor(Extractor):
    def __init__(self, etk: ETK=None, extractor_name: str='date extractor') -> None:
        Extractor.__init__(self,
                           input_type=InputType.TEXT,
                           category="data extractor",
                           name=extractor_name)

        # The 'final_regex' and 'symbol_list' are generated by 'DateRegexGenerator'
        # If the single regexes are changed or more patterns are added,
        # please re-generate 'final_regex' and 'symbol_list' and paste here.
        self.final_regex = {
            "MDY": "(?<=\\b)(?:(?:(?:(?:(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|lunes|martes|mi\u00e9rcoles|jueves|viernes|s\u00e1bado|domingo)|(Mon\\.?|Tue\\.?|Wed\\.?|Thu(?:r(?:s?)?)\\.?|Fri\\.?|Sat\\.?|Sun\\.?|L|M|X|J|V|S|D))(?: of | del | de | el |\\. |, |-|/| ?))?(?:(January|February|March|April|May|June|July|August|September|October|November|December|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)|(Jan\\.?|Feb\\.?|Mar\\.?|Apr\\.?|Jun\\.?|Jul\\.?|Aug\\.?|Sep(?:t?)\\.?|Oct\\.?|Nov\\.?|Dec\\.?|enero|feb\\.?|marzo|abr\\.?|mayo|jun\\.?|jul\\.?|agosto|sept\\.?|set\\.?|oct\\.?|nov\\.?|dic\\.?)|(1[0-2]|0?[1-9]))(?:(?: of | del | de | el |\\. |, |-|/| ?)(?:(3[0-1]|[1-2][0-9]|0?[1-9])|(3[0-1]|[1-2][0-9]|0?[1-9])(?:st|nd|rd|th)))?(?: of | del | de | el |\\. |, |-|/| ?)(?:([1-2][0-9][0-9][0-9])|([6-9][0-9]|[0-3][0-9]))(?:(?: of | del | de | el |\\. |, |-|/| ?)(?:(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|lunes|martes|mi\u00e9rcoles|jueves|viernes|s\u00e1bado|domingo)|(Mon\\.?|Tue\\.?|Wed\\.?|Thu(?:r(?:s?)?)\\.?|Fri\\.?|Sat\\.?|Sun\\.?|L|M|X|J|V|S|D)))?)(?:T?(?:(?: of | del | de | el |\\. |, |-|/| ?)|T)?(?:(?:(1[0-2]|0?[1-9])|(2[0-3]|1[0-9]|0?[0-9])): ?(?:([0-5][0-9]))(?:: ?(?:([0-5][0-9])))?(?:(?:((?: ?)AM(?:\\.?)|(?: ?)PM(?:\\.?))))?(?:(?: of | del | de | el |\\. |, |-|/| ?)(?:(ACDT|ACST|ACT|ACT|ACWST|ADT|AEDT|AEST|AFT|AKDT|AKST|AMST|AMT|AMT|ART|AST|AST|AWST|AZOST|AZOT|AZT|BDT|BIOT|BIT|BOT|BRST|BRT|BST|BST|BST|BTT|CAT|CCT|CDT|CDT|CEST|CET|CHADT|CHAST|CHOT|CHOST|CHST|CHUT|CIST|CIT|CKT|CLST|CLT|COST|COT|CST|CST|CST|CT|CVT|CWST|CXT|DAVT|DDUT|DFT|EASST|EAST|EAT|ECT|ECT|EDT|EEST|EET|EGST|EGT|EIT|EST|FET|FJT|FKST|FKT|FNT|GALT|GAMT|GET|GFT|GILT|GIT|GMT|GST|GST|GYT|HDT|HAEC|HST|HKT|HMT|HOVST|HOVT|ICT|IDT|IOT|IRDT|IRKT|IRST|IST|IST|IST|JST|KGT|KOST|KRAT|KST|LHST|LHST|LINT|MAGT|MART|MAWT|MDT|MET|MEST|MHT|MIST|MIT|MMT|MSK|MST|MST|MUT|MVT|MYT|NCT|NDT|NFT|NPT|NST|NT|NUT|NZDT|NZST|OMST|ORAT|PDT|PET|PETT|PGT|PHOT|PHT|PKT|PMDT|PMST|PONT|PST|PST|PYST|PYT|RET|ROTT|SAKT|SAMT|SAST|SBT|SCT|SDT|SGT|SLST|SRET|SRT|SST|SST|SYOT|TAHT|THA|TFT|TJT|TKT|TLT|TMT|TRT|TOT|TVT|ULAST|ULAT|USZ1|UTC|UYST|UYT|UZT|VET|VLAT|VOLT|VOST|VUT|WAKT|WAST|WAT|WEST|WET|WIT|WST|YAKT|YEKT)|((?:UTC|GMT)(?: ?[\\+\\-] ?(?:(?:1[0-4]|0?[0-9])(?::?(?:00|30|45))?))?|[+-][01][0-3](?:00|30|45)|[\\+\\-](?:1[0-3]|0[0-9])(?:00|30|45))))?)Z?)?)(?=\\b)",
            "DMY": "(?<=\\b)(?:(?:(?:(?:(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|lunes|martes|mi\u00e9rcoles|jueves|viernes|s\u00e1bado|domingo)|(Mon\\.?|Tue\\.?|Wed\\.?|Thu(?:r(?:s?)?)\\.?|Fri\\.?|Sat\\.?|Sun\\.?|L|M|X|J|V|S|D))(?: of | del | de | el |\\. |, |-|/| ?))?(?:(?:(3[0-1]|[1-2][0-9]|0?[1-9])|(3[0-1]|[1-2][0-9]|0?[1-9])(?:st|nd|rd|th))(?: of | del | de | el |\\. |, |-|/| ?))?(?:(January|February|March|April|May|June|July|August|September|October|November|December|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)|(Jan\\.?|Feb\\.?|Mar\\.?|Apr\\.?|Jun\\.?|Jul\\.?|Aug\\.?|Sep(?:t?)\\.?|Oct\\.?|Nov\\.?|Dec\\.?|enero|feb\\.?|marzo|abr\\.?|mayo|jun\\.?|jul\\.?|agosto|sept\\.?|set\\.?|oct\\.?|nov\\.?|dic\\.?)|(1[0-2]|0?[1-9]))(?: of | del | de | el |\\. |, |-|/| ?)(?:([1-2][0-9][0-9][0-9])|([6-9][0-9]|[0-3][0-9]))(?:(?: of | del | de | el |\\. |, |-|/| ?)(?:(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|lunes|martes|mi\u00e9rcoles|jueves|viernes|s\u00e1bado|domingo)|(Mon\\.?|Tue\\.?|Wed\\.?|Thu(?:r(?:s?)?)\\.?|Fri\\.?|Sat\\.?|Sun\\.?|L|M|X|J|V|S|D)))?)(?:T?(?:(?: of | del | de | el |\\. |, |-|/| ?)|T)?(?:(?:(1[0-2]|0?[1-9])|(2[0-3]|1[0-9]|0?[0-9])): ?(?:([0-5][0-9]))(?:: ?(?:([0-5][0-9])))?(?:(?:((?: ?)AM(?:\\.?)|(?: ?)PM(?:\\.?))))?(?:(?: of | del | de | el |\\. |, |-|/| ?)(?:(ACDT|ACST|ACT|ACT|ACWST|ADT|AEDT|AEST|AFT|AKDT|AKST|AMST|AMT|AMT|ART|AST|AST|AWST|AZOST|AZOT|AZT|BDT|BIOT|BIT|BOT|BRST|BRT|BST|BST|BST|BTT|CAT|CCT|CDT|CDT|CEST|CET|CHADT|CHAST|CHOT|CHOST|CHST|CHUT|CIST|CIT|CKT|CLST|CLT|COST|COT|CST|CST|CST|CT|CVT|CWST|CXT|DAVT|DDUT|DFT|EASST|EAST|EAT|ECT|ECT|EDT|EEST|EET|EGST|EGT|EIT|EST|FET|FJT|FKST|FKT|FNT|GALT|GAMT|GET|GFT|GILT|GIT|GMT|GST|GST|GYT|HDT|HAEC|HST|HKT|HMT|HOVST|HOVT|ICT|IDT|IOT|IRDT|IRKT|IRST|IST|IST|IST|JST|KGT|KOST|KRAT|KST|LHST|LHST|LINT|MAGT|MART|MAWT|MDT|MET|MEST|MHT|MIST|MIT|MMT|MSK|MST|MST|MUT|MVT|MYT|NCT|NDT|NFT|NPT|NST|NT|NUT|NZDT|NZST|OMST|ORAT|PDT|PET|PETT|PGT|PHOT|PHT|PKT|PMDT|PMST|PONT|PST|PST|PYST|PYT|RET|ROTT|SAKT|SAMT|SAST|SBT|SCT|SDT|SGT|SLST|SRET|SRT|SST|SST|SYOT|TAHT|THA|TFT|TJT|TKT|TLT|TMT|TRT|TOT|TVT|ULAST|ULAT|USZ1|UTC|UYST|UYT|UZT|VET|VLAT|VOLT|VOST|VUT|WAKT|WAST|WAT|WEST|WET|WIT|WST|YAKT|YEKT)|((?:UTC|GMT)(?: ?[\\+\\-] ?(?:(?:1[0-4]|0?[0-9])(?::?(?:00|30|45))?))?|[+-][01][0-3](?:00|30|45)|[\\+\\-](?:1[0-3]|0[0-9])(?:00|30|45))))?)Z?)?)(?=\\b)",
            "YMD": "(?<=\\b)(?:(?:(?:(?:(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|lunes|martes|mi\u00e9rcoles|jueves|viernes|s\u00e1bado|domingo)|(Mon\\.?|Tue\\.?|Wed\\.?|Thu(?:r(?:s?)?)\\.?|Fri\\.?|Sat\\.?|Sun\\.?|L|M|X|J|V|S|D))(?: of | del | de | el |\\. |, |-|/| ?))?(?:([1-2][0-9][0-9][0-9])|([6-9][0-9]|[0-3][0-9]))(?: of | del | de | el |\\. |, |-|/| ?)(?:(January|February|March|April|May|June|July|August|September|October|November|December|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)|(Jan\\.?|Feb\\.?|Mar\\.?|Apr\\.?|Jun\\.?|Jul\\.?|Aug\\.?|Sep(?:t?)\\.?|Oct\\.?|Nov\\.?|Dec\\.?|enero|feb\\.?|marzo|abr\\.?|mayo|jun\\.?|jul\\.?|agosto|sept\\.?|set\\.?|oct\\.?|nov\\.?|dic\\.?)|(1[0-2]|0?[1-9]))(?:(?: of | del | de | el |\\. |, |-|/| ?)(?:(3[0-1]|[1-2][0-9]|0?[1-9])|(3[0-1]|[1-2][0-9]|0?[1-9])(?:st|nd|rd|th)))?(?:(?: of | del | de | el |\\. |, |-|/| ?)(?:(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|lunes|martes|mi\u00e9rcoles|jueves|viernes|s\u00e1bado|domingo)|(Mon\\.?|Tue\\.?|Wed\\.?|Thu(?:r(?:s?)?)\\.?|Fri\\.?|Sat\\.?|Sun\\.?|L|M|X|J|V|S|D)))?)(?:T?(?:(?: of | del | de | el |\\. |, |-|/| ?)|T)?(?:(?:(1[0-2]|0?[1-9])|(2[0-3]|1[0-9]|0?[0-9])): ?(?:([0-5][0-9]))(?:: ?(?:([0-5][0-9])))?(?:(?:((?: ?)AM(?:\\.?)|(?: ?)PM(?:\\.?))))?(?:(?: of | del | de | el |\\. |, |-|/| ?)(?:(ACDT|ACST|ACT|ACT|ACWST|ADT|AEDT|AEST|AFT|AKDT|AKST|AMST|AMT|AMT|ART|AST|AST|AWST|AZOST|AZOT|AZT|BDT|BIOT|BIT|BOT|BRST|BRT|BST|BST|BST|BTT|CAT|CCT|CDT|CDT|CEST|CET|CHADT|CHAST|CHOT|CHOST|CHST|CHUT|CIST|CIT|CKT|CLST|CLT|COST|COT|CST|CST|CST|CT|CVT|CWST|CXT|DAVT|DDUT|DFT|EASST|EAST|EAT|ECT|ECT|EDT|EEST|EET|EGST|EGT|EIT|EST|FET|FJT|FKST|FKT|FNT|GALT|GAMT|GET|GFT|GILT|GIT|GMT|GST|GST|GYT|HDT|HAEC|HST|HKT|HMT|HOVST|HOVT|ICT|IDT|IOT|IRDT|IRKT|IRST|IST|IST|IST|JST|KGT|KOST|KRAT|KST|LHST|LHST|LINT|MAGT|MART|MAWT|MDT|MET|MEST|MHT|MIST|MIT|MMT|MSK|MST|MST|MUT|MVT|MYT|NCT|NDT|NFT|NPT|NST|NT|NUT|NZDT|NZST|OMST|ORAT|PDT|PET|PETT|PGT|PHOT|PHT|PKT|PMDT|PMST|PONT|PST|PST|PYST|PYT|RET|ROTT|SAKT|SAMT|SAST|SBT|SCT|SDT|SGT|SLST|SRET|SRT|SST|SST|SYOT|TAHT|THA|TFT|TJT|TKT|TLT|TMT|TRT|TOT|TVT|ULAST|ULAT|USZ1|UTC|UYST|UYT|UZT|VET|VLAT|VOLT|VOST|VUT|WAKT|WAST|WAT|WEST|WET|WIT|WST|YAKT|YEKT)|((?:UTC|GMT)(?: ?[\\+\\-] ?(?:(?:1[0-4]|0?[0-9])(?::?(?:00|30|45))?))?|[+-][01][0-3](?:00|30|45)|[\\+\\-](?:1[0-3]|0[0-9])(?:00|30|45))))?)Z?)?)(?=\\b)",
            "SINGLE_MONTH": "(?<=\\b)(?:(?:(?:(January|February|March|April|May|June|July|August|September|October|November|December|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)|(Jan\\.?|Feb\\.?|Mar\\.?|Apr\\.?|Jun\\.?|Jul\\.?|Aug\\.?|Sep(?:t?)\\.?|Oct\\.?|Nov\\.?|Dec\\.?|enero|feb\\.?|marzo|abr\\.?|mayo|jun\\.?|jul\\.?|agosto|sept\\.?|set\\.?|oct\\.?|nov\\.?|dic\\.?)))(?:T?(?:(?: of | del | de | el |\\. |, |-|/| ?)|T)?(?:(?:(1[0-2]|0?[1-9])|(2[0-3]|1[0-9]|0?[0-9])): ?(?:([0-5][0-9]))(?:: ?(?:([0-5][0-9])))?(?:(?:((?: ?)AM(?:\\.?)|(?: ?)PM(?:\\.?))))?(?:(?: of | del | de | el |\\. |, |-|/| ?)(?:(ACDT|ACST|ACT|ACT|ACWST|ADT|AEDT|AEST|AFT|AKDT|AKST|AMST|AMT|AMT|ART|AST|AST|AWST|AZOST|AZOT|AZT|BDT|BIOT|BIT|BOT|BRST|BRT|BST|BST|BST|BTT|CAT|CCT|CDT|CDT|CEST|CET|CHADT|CHAST|CHOT|CHOST|CHST|CHUT|CIST|CIT|CKT|CLST|CLT|COST|COT|CST|CST|CST|CT|CVT|CWST|CXT|DAVT|DDUT|DFT|EASST|EAST|EAT|ECT|ECT|EDT|EEST|EET|EGST|EGT|EIT|EST|FET|FJT|FKST|FKT|FNT|GALT|GAMT|GET|GFT|GILT|GIT|GMT|GST|GST|GYT|HDT|HAEC|HST|HKT|HMT|HOVST|HOVT|ICT|IDT|IOT|IRDT|IRKT|IRST|IST|IST|IST|JST|KGT|KOST|KRAT|KST|LHST|LHST|LINT|MAGT|MART|MAWT|MDT|MET|MEST|MHT|MIST|MIT|MMT|MSK|MST|MST|MUT|MVT|MYT|NCT|NDT|NFT|NPT|NST|NT|NUT|NZDT|NZST|OMST|ORAT|PDT|PET|PETT|PGT|PHOT|PHT|PKT|PMDT|PMST|PONT|PST|PST|PYST|PYT|RET|ROTT|SAKT|SAMT|SAST|SBT|SCT|SDT|SGT|SLST|SRET|SRT|SST|SST|SYOT|TAHT|THA|TFT|TJT|TKT|TLT|TMT|TRT|TOT|TVT|ULAST|ULAT|USZ1|UTC|UYST|UYT|UZT|VET|VLAT|VOLT|VOST|VUT|WAKT|WAST|WAT|WEST|WET|WIT|WST|YAKT|YEKT)|((?:UTC|GMT)(?: ?[\\+\\-] ?(?:(?:1[0-4]|0?[0-9])(?::?(?:00|30|45))?))?|[+-][01][0-3](?:00|30|45)|[\\+\\-](?:1[0-3]|0[0-9])(?:00|30|45))))?)Z?)?)(?=\\b)"
        }
        self.symbol_list = {
            "MDY": ["%A", "%a", "%B", "%b", "%m", "%d", "%d", "%Y", "%y",
                    "%A", "%a", "%I", "%H", "%M", "%S", "%p", "%Z", "%z"],
            "DMY": ["%A", "%a", "%d", "%d", "%B", "%b", "%m", "%Y", "%y",
                    "%A", "%a", "%I", "%H", "%M", "%S", "%p", "%Z", "%z"],
            "YMD": ["%A", "%a", "%Y", "%y", "%B", "%b", "%m", "%d", "%d",
                    "%A", "%a", "%I", "%H", "%M", "%S", "%p", "%Z", "%z"],
            "SINGLE_MONTH": ["%B", "%b", "%I", "%H", "%M", "%S", "%p", "%Z", "%z"]
        }
        self.settings = {}
        self.etk = etk

    def extract(self, text: str = None,
                extract_first_date_only: bool = False,
                additional_formats: List[str] = list(),
                use_default_formats: bool = False,
                ignore_dates_before: datetime.datetime = None,
                ignore_dates_after: datetime.datetime = None,
                detect_relative_dates: bool = True,
                relative_base: datetime.datetime = None,
                preferred_date_order: str = "MDY",
                prefer_language_date_order: bool = True,
                timezone: str = get_localzone().zone,
                to_timezone: str = None,
                return_as_timezone_aware: bool = True,
                prefer_day_of_month: str = "first",
                prefer_dates_from: str = "current"
                ) -> List[Extraction]:
        """

        Args:
            text: str - extract dates from this 'text'
            extract_first_date_only: bool - extract the first valid date only or extract all
            additional_formats: List[str] - user defined formats for extraction
            use_default_formats: bool - if use default formats together with addtional_formats
            ignore_dates_before: datetime.datetime - ignore dates before 'ignore_dates_before'
            ignore_dates_after: datetime.datetime - ignore dates after 'ignore_dates_after'
            detect_relative_dates: bool - if detect relative dates like '9 days before'
            relative_base: datetime.datetime - offset relative dates detected based on 'relative_base'
            preferred_date_order: enum['MDY', 'DMY', 'YMD'] - preferred date order when ambiguous
            prefer_language_date_order: bool - if use the text language's preferred order
            timezone: str - add 'timezone' if there is no timezone information in the extracted date
            to_timezone: str - convert all dates extracted to this timezone
            return_as_timezone_aware: bool - returned datetime timezone awareness
            prefer_day_of_month: enum['first', 'current', 'last'] - use which day of the month when there is no 'day'
            prefer_dates_from: enum['past', 'current', 'future'] - use which date when there is few info(e.g. only month)

        Returns: List[Extraction] - Extraction.value: iso format string
                                    extra attributes in Extraction._provenance:
                                        'date_object': datetime.datetime - the datetime object
                                        'original_text': str - the original str extracted from text
                                        'language': enum['en', 'es'] - language of the date

        """

        if ignore_dates_before and not ignore_dates_before.tzinfo:
            ignore_dates_before = ignore_dates_before.astimezone(pytz.timezone(timezone) if timezone else get_localzone())
        if ignore_dates_after and not ignore_dates_after.tzinfo:
            ignore_dates_after = ignore_dates_after.astimezone(pytz.timezone(timezone) if timezone else get_localzone())
        if relative_base and not relative_base.tzinfo:
            relative_base = relative_base.astimezone(pytz.timezone(timezone) if timezone else get_localzone())

        self.settings = {
            EXTRACT_FIRST_DATE_ONLY: extract_first_date_only,
            ADDITIONAL_FORMATS: additional_formats,
            USE_DEFAULT_FORMATS: use_default_formats,
            IGNORE_DATES_BEFORE: ignore_dates_before,
            IGNORE_DATES_AFTER: ignore_dates_after,
            DETECT_RELATIVE_DATES: detect_relative_dates,
            RELATIVE_BASE: relative_base,
            PREFERRED_DATE_ORDER: preferred_date_order,
            PREFER_LANGUAGE_DATE_ORDER: prefer_language_date_order,
            TIMEZONE: timezone,
            TO_TIMEZONE: to_timezone,
            RETURN_AS_TIMEZONE_AWARE: return_as_timezone_aware,
            PREFER_DAY_OF_MONTH: prefer_day_of_month,
            PREFER_DATES_FROM: prefer_dates_from
        }

        results = []
        additional_regex = []
        if additional_formats:
            for date_format in additional_formats:
                order = ''
                reg = date_format
                for key in singleton_regex:
                    if key[0] == '%':
                        reg2 = re.sub(key, singleton_regex[key], reg)
                        if reg != reg2:
                            if key in units['M']:
                                order += 'M'
                            elif key in units['Y']:
                                order += 'Y'
                            elif key in units['D']:
                                order += 'D'
                            reg = reg2
                additional_regex.append({
                    'reg': reg,
                    'pattern': date_format,
                    'order': order,
                })
            for r in additional_regex:
                matches = [self.wrap_date_match(r['order'], match, pattern=r['pattern']) for
                           match in re.finditer(r['reg'], text, re.I)]
                results.append(matches)
            if use_default_formats:
                for order in self.final_regex.keys():
                    matches = [self.wrap_date_match(order, match) for match
                               in re.finditer(self.final_regex[order], text, re.I) if match]
                    results.append(matches)
        else:
            for order in self.final_regex.keys():
                matches = [self.wrap_date_match(order, match) for match
                           in re.finditer(self.final_regex[order], text, re.I) if match]
                results.append(matches)

        # for absolute dates:
        ans = self.remove_overlapped_date_str(results)
        # for relative dates:
        if detect_relative_dates:
            ans += self.extract_relative_dates(text)

        return ans

    def wrap_extraction(self, date_object: datetime.datetime,
                        original_text: str,
                        start_char: int,
                        end_char: int
                        ) -> Extraction or None:
        """
        wrap the final result as an Extraction and return

        """
        try:
            if not self.settings[RETURN_AS_TIMEZONE_AWARE]:
                # timezone is needed for comparison of the dates,
                # so tzinfo is kept until the dates will be returned
                date_object = date_object.replace(tzinfo=None)
            e = Extraction(self.convert_to_iso_format(date_object),
                           start_char=start_char,
                           end_char=end_char,
                           extractor_name=self.name)
            # need a more elegant way to do this:
            e._provenance['date_object'] = date_object
            e._provenance['original_text'] = original_text
            return e
        except Exception as e:
            print('!Exception', e)
            print(date_object)
            return None

    def remove_overlapped_date_str(self, results: List[List[dict]]) -> List[dict]:
        """
        some string may be matched by multiple date templates,
        deduplicate the results and return a single list

        """
        res = []
        all_results = []
        for x in results:
            all_results = all_results + x
        if not all_results or len(all_results) == 0:
            return list()
        all_results.sort(key=lambda k: k['start'])
        cur_max = all_results[0]
        for x in all_results[1:]:
            if cur_max['end'] <= x['start']:
                parsed_date = self.parse_date(cur_max)
                if parsed_date:
                    if self.settings[EXTRACT_FIRST_DATE_ONLY]:
                        return res
                    res.append(parsed_date)
                cur_max = x
            else:
                if len(x['value']) > len(cur_max['value']):
                    cur_max = x
                elif len(x['value']) == len(cur_max['value']):
                    if self.settings[PREFER_LANGUAGE_DATE_ORDER]:
                        lan = 'en'
                        for token in x['groups']:
                            if token in spanish_to_english:
                                lan = 'es'
                                break
                        if x['order'] == language_date_order[lan]:
                            cur_max = x
                        elif x['order'] == self.settings[PREFERRED_DATE_ORDER]:
                            cur_max = x
                    elif x['order'] == self.settings[PREFERRED_DATE_ORDER]:
                        cur_max = x
        parsed_date = self.parse_date(cur_max)
        if parsed_date:
            if self.settings[EXTRACT_FIRST_DATE_ONLY]:
                return res
            res.append(parsed_date)
        return res

    def parse_date(self, date_info: dict) -> datetime.datetime or None:
        """
        parse a date string extracted to a datetime.datetime object
        apply the customizations like date range, date completion etc.

        """
        miss_day = True
        user_defined_pattern = None

        if date_info['pattern']:
            user_defined_pattern = re.findall(r'%[a-zA-Z]+', date_info['pattern'])

        i = 0
        pattern = list()
        formatted = list()

        for s in date_info['groups']:
            if s:
                p = self.symbol_list[date_info['order']][i] if not user_defined_pattern else user_defined_pattern[i]
                if p in units['D']:
                    miss_day = False
                pattern.append(p)
                formatted_str = s.strip('.').strip().lower()
                if p in ['%B', '%b', '%A', '%a']:
                    if formatted_str in spanish_to_english:
                        formatted_str = spanish_to_english[formatted_str]
                if p in ['%b', '%a']:
                    formatted_str = formatted_str[:3]
                formatted.append(re.sub(r'[^0-9+\-]', '', formatted_str) if p == '%z' else formatted_str)
            i += 1
        date = datetime.datetime.strptime('-'.join(formatted), '-'.join(pattern))

        if miss_day:
            if self.settings[PREFER_DAY_OF_MONTH] == 'current':
                date = date.replace(day=datetime.datetime.now().day)
            elif self.settings[PREFER_DAY_OF_MONTH] == 'last':
                date = date.replace(day=calendar.monthrange(date.year, date.month)[1])

        if date_info['order'] == 'SINGLE_MONTH':
            today = datetime.datetime.now()
            date = date.replace(year=today.year)
            next_year = date.replace(year=today.year+1)
            last_year = date.replace(year=today.year-1)
            if self.settings[PREFER_DATES_FROM] == 'past':
                date = last_year if date > today else date
            elif self.settings[PREFER_DATES_FROM] == 'future':
                date = next_year if date < today else date
            else:
                if date > today and (date-today > today-date.replace(year=today.year-1)):
                    date = last_year
                elif date < today and (today-date < date.replace(year=today.year+1)-today):
                    date = next_year

        if not date.tzinfo:
            try:
                date = date.astimezone(pytz.timezone(self.settings[TIMEZONE]) if self.settings[TIMEZONE] else get_localzone())
            except Exception as e:
                date = date.astimezone(get_localzone())
                print('UnknownTimeZoneError for user defined timezone', self.settings[TIMEZONE])

        try:
            if (self.settings[IGNORE_DATES_BEFORE] and date < self.settings[IGNORE_DATES_BEFORE]) or \
                    (self.settings[IGNORE_DATES_AFTER] and date > self.settings[IGNORE_DATES_AFTER]):
                return None
        except Exception as e:
            print('!Exception: ', e)
            print(self.settings[IGNORE_DATES_BEFORE], self.settings[IGNORE_DATES_BEFORE].tzinfo)
            print(self.settings[IGNORE_DATES_AFTER], self.settings[IGNORE_DATES_AFTER].tzinfo)
            print(date, date.tzinfo)

        if self.settings[TO_TIMEZONE]:
            try:
                date = date.astimezone(pytz.timezone(self.settings[TO_TIMEZONE]))
            except Exception as e:
                date = date.astimezone(get_localzone())
                print(e)
                print('UnknownTimeZoneError for user defined timezone, set to local timezone', self.settings[TIMEZONE])

        return self.wrap_extraction(date, date_info['value'], date_info['start'], date_info['end'])

    def extract_relative_dates(self, text: str) -> List[Extraction]:
        """

        Extract relative dates using spaCy rules

        Args:
            text: str - the text to extract the relative date strings from

        Returns: List of Extraction(s)

        """
        if not text:
            return list()
        base = self.settings[RELATIVE_BASE] if self.settings[RELATIVE_BASE] else datetime.datetime.now()
        res = SpacyRuleExtractor(self.etk.default_nlp, spacy_rules, 'relative_date_extractor').extract(text)
        ans = list()
        for relative_date in res:
            if relative_date.rule_id == 'direction_number_unit':
                direction, measure, unit = relative_date.value.split()
                measure = num_to_digit[measure.lower()]
            elif relative_date.rule_id == 'number_unit_direction':
                measure, unit, direction = relative_date.value.split()
                measure = num_to_digit[measure.lower()]
            elif relative_date.rule_id == 'direction_digit_unit':
                direction, measure, unit = relative_date.value.split()
            elif relative_date.rule_id == 'digit_unit_direction':
                measure, unit, direction = relative_date.value.split()
            elif relative_date.rule_id == 'direction_unit':
                direction, unit = relative_date.value.split()
                measure = '1'
            elif relative_date.rule_id == 'the_day':
                unit = 'days'
                direction = 'ago' if relative_date.value.split()[-1].lower() == 'yesterday' else 'later'
                measure = '1' if len(relative_date.value.split()) == 1 else '2'
            else:
                continue
            unit = unit if unit[-1] == 's' else unit+'s'
            direction = directions[direction.lower()] if direction.lower() in directions else '+'
            delta_args = {unit: int(direction+measure)}
            relative_delta = relativedelta(**delta_args)
            extraction_date = self.wrap_extraction(base+relative_delta,
                                                   relative_date.value,
                                                   relative_date._provenance['start_char'],
                                                   relative_date._provenance['end_char'])
            if extraction_date:
                ans.append(extraction_date)
        return ans

    @staticmethod
    def convert_to_iso_format(date: datetime.datetime, resolution: DateResolution = DateResolution.DAY) -> str or None:
        """

        Args:
            date: datetime.datetime - datetime object to convert
            resolution: resolution of the iso format date to return

        Returns: string of iso format date

        """
        try:
            if date:
                date_str = date.isoformat()
                length = len(date_str)
                if resolution == DateResolution.YEAR and length >= 4:
                    return date_str[:4]
                elif resolution == DateResolution.MONTH and length >= 7:
                    return date_str[:7]
                elif resolution == DateResolution.DAY and length >= 10:
                    return date_str[:10]
                elif resolution == DateResolution.HOUR and length >= 13:
                    return date_str[:13]
                elif resolution == DateResolution.MINUTE and length >= 16:
                    return date_str[:16]
                elif resolution == DateResolution.SECOND and length >= 19:
                    return date_str[:19]
                return date_str
        except Exception as e:
            print('Exception: {}, failed to convert {} to isoformat '.format(e, date))
            return None
        return None

    @staticmethod
    def wrap_date_match(order: str, match: re.match, pattern: str=None) -> dict or None:
        """

        Args:
            order: enums['MDY', 'DMY', 'YMD'] - order of the date
            match: re.match - a regex match object
            pattern: str - if user defined the pattern, record it here

        Returns:

        """
        return {
            'value': match.group(),
            'groups': match.groups(),
            'start': match.start(),
            'end': match.end(),
            'order': order,
            'pattern': pattern
        } if match else None