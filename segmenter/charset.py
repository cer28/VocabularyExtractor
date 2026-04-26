
from segmenter.enums import Charset

charsets = {
    Charset.VIETNAMESE: (r" a-zA-Z"
                         "àáãạảăắằẳẵặâấầẩẫậèéẹẻẽêềếểễệđìíĩỉịòóõọỏôốồổỗộơớờởỡợùúũụủưứừửữựỳỵỷỹý"
                         "ÀÁÃẠẢĂẮẰẲẴẶÂẤẦẨẪẬÈÉẸẺẼÊỀẾỂỄỆĐÌÍĨỈỊÒÓÕỌỎÔỐỒỔỖỘƠỚỜỞỠỢÙÚŨỤỦƯỨỪỬỮỰỲỴỶỸÝ",
                         r"\s+"),
    Charset.CHINESE: (
        "一-鿿"       # CJK Unified Ideographs
        "㐀-䶿"       # CJK Unified Ideographs Extension A
        "豈-﫿"       # CJK Compatibility Ideographs
        "〇"              # Ideographic number zero 〇
        "Ａ-Ｚ"       # Fullwidth Latin uppercase
        "ａ-ｚ",      # Fullwidth Latin lowercase
        '',
    ),
    Charset.ASCII_8: (r" A-Za-z\x80-\xFF", r"\s+"),
}
