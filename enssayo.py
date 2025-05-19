import math

def gms_to_decimal(g, m, s):
    return g + m/60 + s/3600

def rad_to_gms(theta_rad):
    deg_total = math.degrees(theta_rad)
    d = int(deg_total)
    m = int((deg_total - d) * 60)
    s = (deg_total - d - m/60) * 3600
    return d, m, s

EA, NA = (1000.000, 2000.000)
EB, NB = (1078.331, 2077.869)
EC, NC = (1172.191, 2154.753)

AB = math.hypot(NB - NA, EB - EA)
print(AB)
BC = math.hypot(NC - NB, EC - EB)
print(BC)
CA = math.hypot(NC - NA, EC - EA)
print(CA)

x = gms_to_decimal(float(57), float(36), float(0))
xr=math.radians(x)
print(xr)
z = gms_to_decimal(float(40), float(8), float(24))
zr=math.radians(z)
p_hat = z + x
pr = math.radians(p_hat)

        # 2) Ángulos interiores de △ABC usando ley de cosenos
A_hat = math.acos((AB**2 + CA**2 - BC**2) / (2 * AB * CA))

B_hat = math.acos((AB**2 + BC**2 - CA**2) / (2 * AB * BC))

C_hat = math.pi - (A_hat + B_hat)

        # 3) Constante k = (senÂ · BC) / (senĈ · AB)
k = (math.sin(xr) * AB) / (math.sin(zr) * BC)


print((k))