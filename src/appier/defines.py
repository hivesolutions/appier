#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2015 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2015 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import re

ITERABLES = (list, tuple)
""" The tuple that defined the various base types
that are considered to be generally "iterable" """

MOBILE_REGEX = re.compile(r"(android|bb\\d+|meego).+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino", re.I | re.M)
""" The regular expression that is going to be used
to validate the compete user agent string for mobile """

MOBILE_PREFIX_REGEX = re.compile(r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\\-|your|zeto|zte\\-", re.I | re.M)
""" The regular expression to test the base prefix
of the user agent string for mobile browser """

BODY_REGEX = re.compile(r"<body[^<>]*?>(.*?)</body>", re.I)
""" Regular expression that is going to be used in the matching
of the partial contents (child) nodes of a body html node """

TAG_REGEX = re.compile(r"<[^<]*?>")
""" The regular expression that is going to be used in the matching
of an html/xml based node in the html to plain text conversion """

EMAIL_REGEX = re.compile(
    r"((?P<name>^.+) \<(?P<email_a>[\w\d\._%+-]+@[\w\d\.\-]+)\>)|(?P<email_b>[\w\d\._%+-]+@[\w\d\.\-]+)$",
    flags = re.UNICODE
)
""" The regular expression that is going to be used
in the matching of email lines, it supports both the
extended (including name) and the simplified versions """

WINDOWS_LOCALE = dict(
    af = "Afrikaans",
    sq = "Albanian",
    am = "Amharic",
    ar_DZ = "Arabic_Algeria",
    ar_BH = "Arabic_Bahrain",
    ar_EG = "Arabic_Egypt",
    ar_IQ = "Arabic_Iraq",
    ar_JO = "Arabic_Jordan",
    ar_KW = "Arabic_Kuwait",
    ar_LB = "Arabic_Lebanon",
    ar_LY = "Arabic_Libya",
    ar_MA = "Arabic_Morocco",
    ar_OM = "Arabic_Oman",
    ar_QA = "Arabic_Qatar",
    ar_SA = "Arabic_Saudi Arabia",
    ar_SY = "Arabic_Syria",
    ar_TN = "Arabic_Tunisia",
    ar_AE = "Arabic_United Arab Emirates",
    ar_YE = "Arabic_Yemen",
    hy = "Armenian",
    az_AZ = "Azeri_Cyrillic",
    eu = "Basque",
    be = "Belarusian",
    bn = "Bengali_Bangladesh",
    bs = "Bosnian",
    bg = "Bulgarian",
    my = "Burmese",
    ca = "Catalan",
    zh_CN = "Chinese_China",
    zh_HK = "Chinese_Hong Kong SAR",
    zh_MO = "Chinese_Macau SAR",
    zh_SG = "Chinese_Singapore",
    zh_TW = "Chinese_Taiwan",
    hr = "Croatian",
    cs = "Czech",
    da = "Danish",
    dv = "Divehi; Dhivehi; Maldivian",
    nl_BE = "Dutch_Belgium",
    nl_NL = "Dutch_Netherlands",
    en_AU = "English_Australia",
    en_BZ = "English_Belize",
    en_CA = "English_Canada",
    en_CB = "English_Caribbean",
    en_GB = "English_Great Britain",
    en_IN = "English_India",
    en_IE = "English_Ireland",
    en_JM = "English_Jamaica",
    en_NZ = "English_New Zealand",
    en_PH = "English_Phillippines",
    en_ZA = "English_Southern Africa",
    en_TT = "English_Trinidad",
    en_US = "English_United States",
    et = "Estonian",
    fo = "Faroese",
    fa = "Farsi_Persian",
    fi = "Finnish",
    fr_BE = "French_Belgium",
    fr_CA = "French_Canada",
    fr_FR = "French_France",
    fr_LU = "French_Luxembourg",
    fr_CH = "French_Switzerland",
    mk = "FYRO Macedonia",
    gd_IE = "Gaelic_Ireland",
    gd = "Gaelic_Scotland",
    de_AT = "German_Austria",
    de_DE = "German_Germany",
    de_LI = "German_Liechtenstein",
    de_LU = "German_Luxembourg",
    de_CH = "German_Switzerland",
    el = "Greek",
    gn = "Guarani_Paraguay",
    gu = "Gujarati",
    he = "Hebrew",
    hi = "Hindi",
    hu = "Hungarian",
    id = "Indonesian",
    it_IT = "Italian_Italy",
    it_CH = "Italian_Switzerland",
    ja = "Japanese",
    kn = "Kannada",
    ks = "Kashmiri",
    kk = "Kazakh",
    km = "Khmer",
    ko = "Korean",
    lo = "Lao",
    la = "Latin",
    lv = "Latvian",
    lt = "Lithuanian",
    ms_BN = "Malay_Brunei",
    ms_MY = "Malay_Malaysia",
    ml = "Malayalam",
    mt = "Maltese",
    mi = "Maori",
    mr = "Marathi",
    mn = "Mongolian",
    ne = "Nepali",
    no_NO = "Norwegian_Bokml",
    pl = "Polish",
    pt_BR = "Portuguese_Brazil",
    pt_PT = "Portuguese_Portugal",
    pa = "Punjabi",
    rm = "Raeto-Romance",
    ro_MO = "Romanian_Moldova",
    ro = "Romanian_Romania",
    ru = "Russian",
    ru_MO = "Russian_Moldova",
    sa = "Sanskrit",
    sr_SP = "Serbian_Cyrillic",
    tn = "Setsuana",
    sd = "Sindhi",
    si = "Sinhala; Sinhalese",
    sk = "Slovak",
    sl = "Slovenian",
    so = "Somali",
    sb = "Sorbian",
    es_AR = "Spanish_Argentina",
    es_BO = "Spanish_Bolivia",
    es_CL = "Spanish_Chile",
    es_CO = "Spanish_Colombia",
    es_CR = "Spanish_Costa Rica",
    es_DO = "Spanish_Dominican Republic",
    es_EC = "Spanish_Ecuador",
    es_SV = "Spanish_El Salvador",
    es_GT = "Spanish_Guatemala",
    es_HN = "Spanish_Honduras",
    es_MX = "Spanish_Mexico",
    es_NI = "Spanish_Nicaragua",
    es_PA = "Spanish_Panama",
    es_PY = "Spanish_Paraguay",
    es_PE = "Spanish_Peru",
    es_PR = "Spanish_Puerto Rico",
    es_ES = "Spanish_Spain (Traditional)",
    es_UY = "Spanish_Uruguay",
    es_VE = "Spanish_Venezuela",
    sw = "Swahili",
    sv_FI = "Swedish_Finland",
    sv_SE = "Swedish_Sweden",
    tg = "Tajik",
    ta = "Tamil",
    tt = "Tatar",
    te = "Telugu",
    th = "Thai",
    bo = "Tibetan",
    ts = "Tsonga",
    tr = "Turkish",
    tk = "Turkmen",
    uk = "Ukrainian",
    UTF_8 = "Unicode",
    ur = "Urdu",
    uz_UZ = "Uzbek_Cyrillic",
    vi = "Vietnamese",
    cy = "Welsh",
    xh = "Xhosa",
    yi = "Yiddish",
    zu = "Zulu"
)
""" The map containing the associations between the
normalized version/descriptor of the locale and the
longer windows version of them so that it may be used
when setting locales for windows based operative systems """
