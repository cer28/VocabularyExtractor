
from segmenter.enums import Charset

charsets = {
    Charset.VIETNAMESE: (r" a-zA-Z"
                         "àáãạảăắằẳẵặâấầẩẫậèéẹẻẽêềếểễệđìíĩỉịòóõọỏôốồổỗộơớờởỡợùúũụủưứừửữựỳỵỷỹý"
                         "ÀÁÃẠẢĂẮẰẲẴẶÂẤẦẨẪẬÈÉẸẺẼÊỀẾỂỄỆĐÌÍĨỈỊÒÓÕỌỎÔỐỒỔỖỘƠỚỜỞỠỢÙÚŨỤỦƯỨỪỬỮỰỲỴỶỸÝ",
                         r"\s+"),
    Charset.ENGLISH: (" A-Za-z", r"\s+"),
}
