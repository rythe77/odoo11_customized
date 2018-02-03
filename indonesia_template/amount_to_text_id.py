# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)

#-------------------------------------------------------------
#Indonesian
#-------------------------------------------------------------

to_19 = ( 'Nol',  'Satu',   'Dua',  'Tiga', 'Empat',   'Lima',   'Enam',
          'Tujuh', 'Delapan', 'Sembilan', 'Sepuluh',   'Sebelas', 'Dua Belas', 'Tiga Belas',
          'Empat Belas', 'Lima Belas', 'Enam Belas', 'Tujuh Belas', 'Delapan Belas', 'Sembilan Belas' )
tens  = ( 'Dua Puluh', 'Tiga Puluh', 'Empat Puluh', 'Lima Puluh', 'Enam Puluh', 'Tujuh Puluh', 'Delapan Puluh', 'Sembilan Puluh')
denom = ( '',
          'Ribu',     'Juta',         'Miliar',       'Triliun',       'Kuadriliun',
          'Kuantiliun',  'Sekstiliun',      'Septiliun',    'Oktiliun',      'Noniliun',
          'Desiliun',    'Undesiliun',     'Duodesiliun',  'Tridesiliun',   'Kuatordesiliun',
          'Seksdesiliun', 'Septendesiliun', 'Oktodesiliun', 'Novemdesiliun', 'Vigintiliun' )

def _convert_nn(val):
    """convert a value < 100 to Indonesian.
    """
    if val < 20:
        return to_19[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens)):
        if dval + 10 > val:
            if val % 10:
                return dcap + ' ' + to_19[val % 10]
            return dcap

def _convert_nnn(val):
    """
        convert a value < 1000 to Indonesian, special cased because it is the level that kicks 
        off the < 100 special case.  The rest are more general.
    """
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem == 1:
        word = 'Seratus'
        if mod > 0:
            word += ' '
    if rem > 1:
        word = to_19[rem] + ' Ratus'
        if mod > 0:
            word += ' '
    if mod > 0:
        word += _convert_nn(mod)
    return word

def indonesian_number(val):
    if val < 100:
        return _convert_nn(val)
    if val < 1000:
        return _convert_nnn(val)
    if val < 2000:
        word_thousands = 'Seribu'
        word_rest = _convert_nnn(val-1000)
        ret = word_thousands + ' ' + word_rest
        return ret
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            ret = _convert_nnn(l) + ' ' + denom[didx]
            if r > 0:
                ret = ret + ' ' + indonesian_number(r)
            return ret

def amount_to_text(number):
    number = '%.2f' % number
    units_name = 'Rupiah'
    split_number = str(number).split('.')
    start_word = indonesian_number(int(split_number[0]))

    return start_word + ' ' + units_name