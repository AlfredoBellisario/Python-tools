h = 4.13566733e-15 # eV s
c = 299792458.0 # m / s

def ev_to_nm(ev):
    return h*c/ev*1.0e9

def nm_to_ev(nm):
    return h*c/(nm*1.0e-9)
