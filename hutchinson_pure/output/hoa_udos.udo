; ============================================================
; hoa_udos.udo — HOA Encoding UDOs ordini 1-7
; Formato: AmbiX SN3D/ACN
; Fonte: Angelo Farina angelofarina.it/Aurora/HOA_explicit_formulas.htm
; Generato da generate_hoa_udos.py — verificato con scipy.special
; ============================================================
; Canali per ordine: (N+1)^2
;   ordine 1 ->  4 canali   ordine 5 -> 36 canali
;   ordine 2 ->  9 canali   ordine 6 -> 49 canali
;   ordine 3 -> 16 canali   ordine 7 -> 64 canali
;   ordine 4 -> 25 canali
; ============================================================

; ── Ordine 1 — 4 canali ─────────────────────────────
opcode hoa_encode_1, aaaa, aaa
  asig, aAzi, aEle xin

  ; Trig k-rate
  kS  = sin(aEle)
  kC  = cos(aEle)
  kSa = sin(aAzi)
  kCa = cos(aAzi)

  aACN00 = asig * (1)
  aACN01 = asig * (kSa * kC)
  aACN02 = asig * (kS)
  aACN03 = asig * (kCa * kC)

  xout aACN00, aACN01, aACN02, aACN03
endop
; ── Ordine 2 — 9 canali ─────────────────────────────
opcode hoa_encode_2, aaaaaaaaa, aaa
  asig, aAzi, aEle xin

  ; Trig k-rate
  kS  = sin(aEle)
  kC  = cos(aEle)
  kSa = sin(aAzi)
  kCa = cos(aAzi)
  kC2 = kC * kC
  kS2 = kS * kS
  kSa2 = kSa * kSa
  kCa2 = kCa * kCa

  aACN00 = asig * (1)
  aACN01 = asig * (kSa * kC)
  aACN02 = asig * (kS)
  aACN03 = asig * (kCa * kC)
  aACN04 = asig * (sqrt(3) * kSa * kCa * kC2)
  aACN05 = asig * (sqrt(3) * kSa * kS * kC)
  aACN06 = asig * ((3*kS2 - 1) / 2)
  aACN07 = asig * (sqrt(3) * kCa * kS * kC)
  aACN08 = asig * (sqrt(3)/2 * (kCa2 - kSa2) * kC2)

  xout aACN00, aACN01, aACN02, aACN03, aACN04, aACN05, aACN06, aACN07, aACN08
endop
; ── Ordine 3 — 16 canali ─────────────────────────────
opcode hoa_encode_3, aaaaaaaaaaaaaaaa, aaa
  asig, aAzi, aEle xin

  ; Trig k-rate
  kS  = sin(aEle)
  kC  = cos(aEle)
  kSa = sin(aAzi)
  kCa = cos(aAzi)
  kC2 = kC * kC
  kC3 = kC2 * kC
  kS2 = kS * kS
  kS3 = kS2 * kS
  kSa2 = kSa * kSa
  kCa2 = kCa * kCa

  aACN00 = asig * (1)
  aACN01 = asig * (kSa * kC)
  aACN02 = asig * (kS)
  aACN03 = asig * (kCa * kC)
  aACN04 = asig * (sqrt(3) * kSa * kCa * kC2)
  aACN05 = asig * (sqrt(3) * kSa * kS * kC)
  aACN06 = asig * ((3*kS2 - 1) / 2)
  aACN07 = asig * (sqrt(3) * kCa * kS * kC)
  aACN08 = asig * (sqrt(3)/2 * (kCa2 - kSa2) * kC2)
  aACN09 = asig * (sqrt(10)/4 * kSa * (3*kCa2 - kSa2) * kC3)
  aACN10 = asig * (sqrt(15) * kSa * kCa * kS * kC2)
  aACN11 = asig * (sqrt(6)/4 * kSa * kC * (5*kS2 - 1))
  aACN12 = asig * ((5*kS3 - 3*kS) / 2)
  aACN13 = asig * (sqrt(6)/4 * kCa * kC * (5*kS2 - 1))
  aACN14 = asig * (sqrt(15)/2 * (kCa2 - kSa2) * kS * kC2)
  aACN15 = asig * (sqrt(10)/4 * kCa * (kCa2 - 3*kSa2) * kC3)

  xout aACN00, aACN01, aACN02, aACN03, aACN04, aACN05, aACN06, aACN07, aACN08, aACN09, aACN10, aACN11, aACN12, aACN13, aACN14, aACN15
endop
; ── Ordine 4 — 25 canali ─────────────────────────────
opcode hoa_encode_4, aaaaaaaaaaaaaaaaaaaaaaaaa, aaa
  asig, aAzi, aEle xin

  ; Trig k-rate
  kS  = sin(aEle)
  kC  = cos(aEle)
  kSa = sin(aAzi)
  kCa = cos(aAzi)
  kC2 = kC * kC
  kC3 = kC2 * kC
  kC4 = kC3 * kC
  kS2 = kS * kS
  kS3 = kS2 * kS
  kS4 = kS3 * kS
  kSa2 = kSa * kSa
  kCa2 = kCa * kCa
  kSa4 = kSa2 * kSa2
  kCa4 = kCa2 * kCa2

  aACN00 = asig * (1)
  aACN01 = asig * (kSa * kC)
  aACN02 = asig * (kS)
  aACN03 = asig * (kCa * kC)
  aACN04 = asig * (sqrt(3) * kSa * kCa * kC2)
  aACN05 = asig * (sqrt(3) * kSa * kS * kC)
  aACN06 = asig * ((3*kS2 - 1) / 2)
  aACN07 = asig * (sqrt(3) * kCa * kS * kC)
  aACN08 = asig * (sqrt(3)/2 * (kCa2 - kSa2) * kC2)
  aACN09 = asig * (sqrt(10)/4 * kSa * (3*kCa2 - kSa2) * kC3)
  aACN10 = asig * (sqrt(15) * kSa * kCa * kS * kC2)
  aACN11 = asig * (sqrt(6)/4 * kSa * kC * (5*kS2 - 1))
  aACN12 = asig * ((5*kS3 - 3*kS) / 2)
  aACN13 = asig * (sqrt(6)/4 * kCa * kC * (5*kS2 - 1))
  aACN14 = asig * (sqrt(15)/2 * (kCa2 - kSa2) * kS * kC2)
  aACN15 = asig * (sqrt(10)/4 * kCa * (kCa2 - 3*kSa2) * kC3)
  aACN16 = asig * (sqrt(35)/2 * kSa * kCa * (kCa2 - kSa2) * kC4)
  aACN17 = asig * (sqrt(70)/4 * kSa * (3*kCa2 - kSa2) * kS * kC3)
  aACN18 = asig * (sqrt(5)/2 * kSa * kCa * kC2 * (7*kS2 - 1))
  aACN19 = asig * (sqrt(10)/4 * kSa * kS * kC * (7*kS2 - 3))
  aACN20 = asig * ((35*kS4 - 30*kS2 + 3) / 8)
  aACN21 = asig * (sqrt(10)/4 * kCa * kS * kC * (7*kS2 - 3))
  aACN22 = asig * (sqrt(5)/4 * (kCa2 - kSa2) * kC2 * (7*kS2 - 1))
  aACN23 = asig * (sqrt(70)/4 * kCa * (kCa2 - 3*kSa2) * kS * kC3)
  aACN24 = asig * (sqrt(35)/8 * ((kCa2-kSa2) ^ 2 - 4*kCa2*kSa2) * kC4)

  xout aACN00, aACN01, aACN02, aACN03, aACN04, aACN05, aACN06, aACN07, aACN08, aACN09, aACN10, aACN11, aACN12, aACN13, aACN14, aACN15, aACN16, aACN17, aACN18, aACN19, aACN20, aACN21, aACN22, aACN23, aACN24
endop
; ── Ordine 5 — 36 canali ─────────────────────────────
opcode hoa_encode_5, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, aaa
  asig, aAzi, aEle xin

  ; Trig k-rate
  kS  = sin(aEle)
  kC  = cos(aEle)
  kSa = sin(aAzi)
  kCa = cos(aAzi)
  kC2 = kC * kC
  kC3 = kC2 * kC
  kC4 = kC3 * kC
  kC5 = kC4 * kC
  kS2 = kS * kS
  kS3 = kS2 * kS
  kS4 = kS3 * kS
  kS5 = kS4 * kS
  kSa2 = kSa * kSa
  kCa2 = kCa * kCa
  kSa4 = kSa2 * kSa2
  kCa4 = kCa2 * kCa2

  aACN00 = asig * (1)
  aACN01 = asig * (kSa * kC)
  aACN02 = asig * (kS)
  aACN03 = asig * (kCa * kC)
  aACN04 = asig * (sqrt(3) * kSa * kCa * kC2)
  aACN05 = asig * (sqrt(3) * kSa * kS * kC)
  aACN06 = asig * ((3*kS2 - 1) / 2)
  aACN07 = asig * (sqrt(3) * kCa * kS * kC)
  aACN08 = asig * (sqrt(3)/2 * (kCa2 - kSa2) * kC2)
  aACN09 = asig * (sqrt(10)/4 * kSa * (3*kCa2 - kSa2) * kC3)
  aACN10 = asig * (sqrt(15) * kSa * kCa * kS * kC2)
  aACN11 = asig * (sqrt(6)/4 * kSa * kC * (5*kS2 - 1))
  aACN12 = asig * ((5*kS3 - 3*kS) / 2)
  aACN13 = asig * (sqrt(6)/4 * kCa * kC * (5*kS2 - 1))
  aACN14 = asig * (sqrt(15)/2 * (kCa2 - kSa2) * kS * kC2)
  aACN15 = asig * (sqrt(10)/4 * kCa * (kCa2 - 3*kSa2) * kC3)
  aACN16 = asig * (sqrt(35)/2 * kSa * kCa * (kCa2 - kSa2) * kC4)
  aACN17 = asig * (sqrt(70)/4 * kSa * (3*kCa2 - kSa2) * kS * kC3)
  aACN18 = asig * (sqrt(5)/2 * kSa * kCa * kC2 * (7*kS2 - 1))
  aACN19 = asig * (sqrt(10)/4 * kSa * kS * kC * (7*kS2 - 3))
  aACN20 = asig * ((35*kS4 - 30*kS2 + 3) / 8)
  aACN21 = asig * (sqrt(10)/4 * kCa * kS * kC * (7*kS2 - 3))
  aACN22 = asig * (sqrt(5)/4 * (kCa2 - kSa2) * kC2 * (7*kS2 - 1))
  aACN23 = asig * (sqrt(70)/4 * kCa * (kCa2 - 3*kSa2) * kS * kC3)
  aACN24 = asig * (sqrt(35)/8 * ((kCa2-kSa2) ^ 2 - 4*kCa2*kSa2) * kC4)
  aACN25 = asig * (sqrt(126)/16 * kC5 * (kSa*(5*kCa4 - 10*kCa2*kSa2 + kSa4)))
  aACN26 = asig * (sqrt(315)/8 * kS * kC4 * (4*kSa*kCa*(kCa2 - kSa2)))
  aACN27 = asig * ((-sqrt(70)/16 * kC3 + 4.70621265 * kS2 * kC3) * (kSa*(3*kCa2 - kSa2)))
  aACN28 = asig * ((-sqrt(105)/4 * kS * kC2 + 7.68521307 * kS3 * kC2) * (2*kSa*kCa))
  aACN29 = asig * ((sqrt(15)/8 * kC + -6.77772086 * kS2 * kC + 10.16658128 * kS4 * kC) * kSa)
  aACN30 = asig * ((sqrt(225)/8 * kS + -8.75000000 * kS3 + 7.87500000 * kS5))
  aACN31 = asig * ((sqrt(15)/8 * kC + -6.77772086 * kS2 * kC + 10.16658128 * kS4 * kC) * kCa)
  aACN32 = asig * ((-sqrt(105)/4 * kS * kC2 + 7.68521307 * kS3 * kC2) * (kCa2 - kSa2))
  aACN33 = asig * ((-sqrt(70)/16 * kC3 + 4.70621265 * kS2 * kC3) * (kCa*(kCa2 - 3*kSa2)))
  aACN34 = asig * (sqrt(315)/8 * kS * kC4 * ((kCa2 - kSa2) ^ 2 - 4*kCa2*kSa2))
  aACN35 = asig * (sqrt(126)/16 * kC5 * (kCa*(kCa4 - 10*kCa2*kSa2 + 5*kSa4)))

  xout aACN00, aACN01, aACN02, aACN03, aACN04, aACN05, aACN06, aACN07, aACN08, aACN09, aACN10, aACN11, aACN12, aACN13, aACN14, aACN15, aACN16, aACN17, aACN18, aACN19, aACN20, aACN21, aACN22, aACN23, aACN24, aACN25, aACN26, aACN27, aACN28, aACN29, aACN30, aACN31, aACN32, aACN33, aACN34, aACN35
endop
; ── Ordine 6 — 49 canali ─────────────────────────────
opcode hoa_encode_6, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, aaa
  asig, aAzi, aEle xin

  ; Trig k-rate
  kS  = sin(aEle)
  kC  = cos(aEle)
  kSa = sin(aAzi)
  kCa = cos(aAzi)
  kC2 = kC * kC
  kC3 = kC2 * kC
  kC4 = kC3 * kC
  kC5 = kC4 * kC
  kC6 = kC5 * kC
  kS2 = kS * kS
  kS3 = kS2 * kS
  kS4 = kS3 * kS
  kS5 = kS4 * kS
  kS6 = kS5 * kS
  kSa2 = kSa * kSa
  kCa2 = kCa * kCa
  kSa4 = kSa2 * kSa2
  kCa4 = kCa2 * kCa2
  kSa6 = kSa4 * kSa2
  kCa6 = kCa4 * kCa2

  aACN00 = asig * (1)
  aACN01 = asig * (kSa * kC)
  aACN02 = asig * (kS)
  aACN03 = asig * (kCa * kC)
  aACN04 = asig * (sqrt(3) * kSa * kCa * kC2)
  aACN05 = asig * (sqrt(3) * kSa * kS * kC)
  aACN06 = asig * ((3*kS2 - 1) / 2)
  aACN07 = asig * (sqrt(3) * kCa * kS * kC)
  aACN08 = asig * (sqrt(3)/2 * (kCa2 - kSa2) * kC2)
  aACN09 = asig * (sqrt(10)/4 * kSa * (3*kCa2 - kSa2) * kC3)
  aACN10 = asig * (sqrt(15) * kSa * kCa * kS * kC2)
  aACN11 = asig * (sqrt(6)/4 * kSa * kC * (5*kS2 - 1))
  aACN12 = asig * ((5*kS3 - 3*kS) / 2)
  aACN13 = asig * (sqrt(6)/4 * kCa * kC * (5*kS2 - 1))
  aACN14 = asig * (sqrt(15)/2 * (kCa2 - kSa2) * kS * kC2)
  aACN15 = asig * (sqrt(10)/4 * kCa * (kCa2 - 3*kSa2) * kC3)
  aACN16 = asig * (sqrt(35)/2 * kSa * kCa * (kCa2 - kSa2) * kC4)
  aACN17 = asig * (sqrt(70)/4 * kSa * (3*kCa2 - kSa2) * kS * kC3)
  aACN18 = asig * (sqrt(5)/2 * kSa * kCa * kC2 * (7*kS2 - 1))
  aACN19 = asig * (sqrt(10)/4 * kSa * kS * kC * (7*kS2 - 3))
  aACN20 = asig * ((35*kS4 - 30*kS2 + 3) / 8)
  aACN21 = asig * (sqrt(10)/4 * kCa * kS * kC * (7*kS2 - 3))
  aACN22 = asig * (sqrt(5)/4 * (kCa2 - kSa2) * kC2 * (7*kS2 - 1))
  aACN23 = asig * (sqrt(70)/4 * kCa * (kCa2 - 3*kSa2) * kS * kC3)
  aACN24 = asig * (sqrt(35)/8 * ((kCa2-kSa2) ^ 2 - 4*kCa2*kSa2) * kC4)
  aACN25 = asig * (sqrt(126)/16 * kC5 * (kSa*(5*kCa4 - 10*kCa2*kSa2 + kSa4)))
  aACN26 = asig * (sqrt(315)/8 * kS * kC4 * (4*kSa*kCa*(kCa2 - kSa2)))
  aACN27 = asig * ((-sqrt(70)/16 * kC3 + 4.70621265 * kS2 * kC3) * (kSa*(3*kCa2 - kSa2)))
  aACN28 = asig * ((-sqrt(105)/4 * kS * kC2 + 7.68521307 * kS3 * kC2) * (2*kSa*kCa))
  aACN29 = asig * ((sqrt(15)/8 * kC + -6.77772086 * kS2 * kC + 10.16658128 * kS4 * kC) * kSa)
  aACN30 = asig * ((sqrt(225)/8 * kS + -8.75000000 * kS3 + 7.87500000 * kS5))
  aACN31 = asig * ((sqrt(15)/8 * kC + -6.77772086 * kS2 * kC + 10.16658128 * kS4 * kC) * kCa)
  aACN32 = asig * ((-sqrt(105)/4 * kS * kC2 + 7.68521307 * kS3 * kC2) * (kCa2 - kSa2))
  aACN33 = asig * ((-sqrt(70)/16 * kC3 + 4.70621265 * kS2 * kC3) * (kCa*(kCa2 - 3*kSa2)))
  aACN34 = asig * (sqrt(315)/8 * kS * kC4 * ((kCa2 - kSa2) ^ 2 - 4*kCa2*kSa2))
  aACN35 = asig * (sqrt(126)/16 * kC5 * (kCa*(kCa4 - 10*kCa2*kSa2 + 5*kSa4)))
  aACN36 = asig * (sqrt(462)/32 * kC6 * (2*kSa*kCa*(3*kCa4 - 10*kCa2*kSa2 + 3*kSa4)))
  aACN37 = asig * (2.32681381 * kS * kC5 * (kSa*(5*kCa4 - 10*kCa2*kSa2 + kSa4)))
  aACN38 = asig * ((-sqrt(63)/16 * kC4 + 5.45686208 * kS2 * kC4) * (4*kSa*kCa*(kCa2 - kSa2)))
  aACN39 = asig * ((-2.71713314 * kS * kC3 + 9.96282151 * kS3 * kC3) * (kSa*(3*kCa2 - kSa2)))
  aACN40 = asig * ((sqrt(210)/32 * kC2 + -8.15139942 * kS2 * kC2 + 14.94423227 * kS4 * kC2) * (2*kSa*kCa))
  aACN41 = asig * ((2.86410981 * kS * kC + -17.18465886 * kS3 * kC + 18.90312474 * kS5 * kC) * kSa)
  aACN42 = asig * ((-sqrt(25)/16 + 6.56250000 * kS2 + -19.68750000 * kS4 + 14.43750000 * kS6))
  aACN43 = asig * ((2.86410981 * kS * kC + -17.18465886 * kS3 * kC + 18.90312474 * kS5 * kC) * kCa)
  aACN44 = asig * ((sqrt(210)/32 * kC2 + -8.15139942 * kS2 * kC2 + 14.94423227 * kS4 * kC2) * (kCa2 - kSa2))
  aACN45 = asig * ((-2.71713314 * kS * kC3 + 9.96282151 * kS3 * kC3) * (kCa*(kCa2 - 3*kSa2)))
  aACN46 = asig * ((-sqrt(63)/16 * kC4 + 5.45686208 * kS2 * kC4) * ((kCa2 - kSa2) ^ 2 - 4*kCa2*kSa2))
  aACN47 = asig * (2.32681381 * kS * kC5 * (kCa*(kCa4 - 10*kCa2*kSa2 + 5*kSa4)))
  aACN48 = asig * (sqrt(462)/32 * kC6 * (kCa6 - 15*kCa4*kSa2 + 15*kCa2*kSa4 - kSa6))

  xout aACN00, aACN01, aACN02, aACN03, aACN04, aACN05, aACN06, aACN07, aACN08, aACN09, aACN10, aACN11, aACN12, aACN13, aACN14, aACN15, aACN16, aACN17, aACN18, aACN19, aACN20, aACN21, aACN22, aACN23, aACN24, aACN25, aACN26, aACN27, aACN28, aACN29, aACN30, aACN31, aACN32, aACN33, aACN34, aACN35, aACN36, aACN37, aACN38, aACN39, aACN40, aACN41, aACN42, aACN43, aACN44, aACN45, aACN46, aACN47, aACN48
endop
; ── Ordine 7 — 64 canali ─────────────────────────────
opcode hoa_encode_7, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa, aaa
  asig, aAzi, aEle xin

  ; Trig k-rate
  kS  = sin(aEle)
  kC  = cos(aEle)
  kSa = sin(aAzi)
  kCa = cos(aAzi)
  kC2 = kC * kC
  kC3 = kC2 * kC
  kC4 = kC3 * kC
  kC5 = kC4 * kC
  kC6 = kC5 * kC
  kC7 = kC6 * kC
  kS2 = kS * kS
  kS3 = kS2 * kS
  kS4 = kS3 * kS
  kS5 = kS4 * kS
  kS6 = kS5 * kS
  kS7 = kS6 * kS
  kSa2 = kSa * kSa
  kCa2 = kCa * kCa
  kSa4 = kSa2 * kSa2
  kCa4 = kCa2 * kCa2
  kSa6 = kSa4 * kSa2
  kCa6 = kCa4 * kCa2

  aACN00 = asig * (1)
  aACN01 = asig * (kSa * kC)
  aACN02 = asig * (kS)
  aACN03 = asig * (kCa * kC)
  aACN04 = asig * (sqrt(3) * kSa * kCa * kC2)
  aACN05 = asig * (sqrt(3) * kSa * kS * kC)
  aACN06 = asig * ((3*kS2 - 1) / 2)
  aACN07 = asig * (sqrt(3) * kCa * kS * kC)
  aACN08 = asig * (sqrt(3)/2 * (kCa2 - kSa2) * kC2)
  aACN09 = asig * (sqrt(10)/4 * kSa * (3*kCa2 - kSa2) * kC3)
  aACN10 = asig * (sqrt(15) * kSa * kCa * kS * kC2)
  aACN11 = asig * (sqrt(6)/4 * kSa * kC * (5*kS2 - 1))
  aACN12 = asig * ((5*kS3 - 3*kS) / 2)
  aACN13 = asig * (sqrt(6)/4 * kCa * kC * (5*kS2 - 1))
  aACN14 = asig * (sqrt(15)/2 * (kCa2 - kSa2) * kS * kC2)
  aACN15 = asig * (sqrt(10)/4 * kCa * (kCa2 - 3*kSa2) * kC3)
  aACN16 = asig * (sqrt(35)/2 * kSa * kCa * (kCa2 - kSa2) * kC4)
  aACN17 = asig * (sqrt(70)/4 * kSa * (3*kCa2 - kSa2) * kS * kC3)
  aACN18 = asig * (sqrt(5)/2 * kSa * kCa * kC2 * (7*kS2 - 1))
  aACN19 = asig * (sqrt(10)/4 * kSa * kS * kC * (7*kS2 - 3))
  aACN20 = asig * ((35*kS4 - 30*kS2 + 3) / 8)
  aACN21 = asig * (sqrt(10)/4 * kCa * kS * kC * (7*kS2 - 3))
  aACN22 = asig * (sqrt(5)/4 * (kCa2 - kSa2) * kC2 * (7*kS2 - 1))
  aACN23 = asig * (sqrt(70)/4 * kCa * (kCa2 - 3*kSa2) * kS * kC3)
  aACN24 = asig * (sqrt(35)/8 * ((kCa2-kSa2) ^ 2 - 4*kCa2*kSa2) * kC4)
  aACN25 = asig * (sqrt(126)/16 * kC5 * (kSa*(5*kCa4 - 10*kCa2*kSa2 + kSa4)))
  aACN26 = asig * (sqrt(315)/8 * kS * kC4 * (4*kSa*kCa*(kCa2 - kSa2)))
  aACN27 = asig * ((-sqrt(70)/16 * kC3 + 4.70621265 * kS2 * kC3) * (kSa*(3*kCa2 - kSa2)))
  aACN28 = asig * ((-sqrt(105)/4 * kS * kC2 + 7.68521307 * kS3 * kC2) * (2*kSa*kCa))
  aACN29 = asig * ((sqrt(15)/8 * kC + -6.77772086 * kS2 * kC + 10.16658128 * kS4 * kC) * kSa)
  aACN30 = asig * ((sqrt(225)/8 * kS + -8.75000000 * kS3 + 7.87500000 * kS5))
  aACN31 = asig * ((sqrt(15)/8 * kC + -6.77772086 * kS2 * kC + 10.16658128 * kS4 * kC) * kCa)
  aACN32 = asig * ((-sqrt(105)/4 * kS * kC2 + 7.68521307 * kS3 * kC2) * (kCa2 - kSa2))
  aACN33 = asig * ((-sqrt(70)/16 * kC3 + 4.70621265 * kS2 * kC3) * (kCa*(kCa2 - 3*kSa2)))
  aACN34 = asig * (sqrt(315)/8 * kS * kC4 * ((kCa2 - kSa2) ^ 2 - 4*kCa2*kSa2))
  aACN35 = asig * (sqrt(126)/16 * kC5 * (kCa*(kCa4 - 10*kCa2*kSa2 + 5*kSa4)))
  aACN36 = asig * (sqrt(462)/32 * kC6 * (2*kSa*kCa*(3*kCa4 - 10*kCa2*kSa2 + 3*kSa4)))
  aACN37 = asig * (2.32681381 * kS * kC5 * (kSa*(5*kCa4 - 10*kCa2*kSa2 + kSa4)))
  aACN38 = asig * ((-sqrt(63)/16 * kC4 + 5.45686208 * kS2 * kC4) * (4*kSa*kCa*(kCa2 - kSa2)))
  aACN39 = asig * ((-2.71713314 * kS * kC3 + 9.96282151 * kS3 * kC3) * (kSa*(3*kCa2 - kSa2)))
  aACN40 = asig * ((sqrt(210)/32 * kC2 + -8.15139942 * kS2 * kC2 + 14.94423227 * kS4 * kC2) * (2*kSa*kCa))
  aACN41 = asig * ((2.86410981 * kS * kC + -17.18465886 * kS3 * kC + 18.90312474 * kS5 * kC) * kSa)
  aACN42 = asig * ((-sqrt(25)/16 + 6.56250000 * kS2 + -19.68750000 * kS4 + 14.43750000 * kS6))
  aACN43 = asig * ((2.86410981 * kS * kC + -17.18465886 * kS3 * kC + 18.90312474 * kS5 * kC) * kCa)
  aACN44 = asig * ((sqrt(210)/32 * kC2 + -8.15139942 * kS2 * kC2 + 14.94423227 * kS4 * kC2) * (kCa2 - kSa2))
  aACN45 = asig * ((-2.71713314 * kS * kC3 + 9.96282151 * kS3 * kC3) * (kCa*(kCa2 - 3*kSa2)))
  aACN46 = asig * ((-sqrt(63)/16 * kC4 + 5.45686208 * kS2 * kC4) * ((kCa2 - kSa2) ^ 2 - 4*kCa2*kSa2))
  aACN47 = asig * (2.32681381 * kS * kC5 * (kCa*(kCa4 - 10*kCa2*kSa2 + 5*kSa4)))
  aACN48 = asig * (sqrt(462)/32 * kC6 * (kCa6 - 15*kCa4*kSa2 + 15*kCa2*kSa4 - kSa6))
  aACN49 = asig * (sqrt(429)/32 * kC7 * (kSa*(7*kCa6 - 35*kCa4*kSa2 + 21*kCa2*kSa4 - kSa6)))
  aACN50 = asig * (2.42182460 * kS * kC6 * (2*kSa*kCa*(3*kCa4 - 10*kCa2*kSa2 + 3*kSa4)))
  aACN51 = asig * ((-sqrt(231)/32 * kC5 + 6.17446544 * kS2 * kC5) * (kSa*(5*kCa4 - 10*kCa2*kSa2 + kSa4)))
  aACN52 = asig * ((-2.84975328 * kS * kC4 + 12.34893087 * kS3 * kC4) * (4*kSa*kCa*(kCa2 - kSa2)))
  aACN53 = asig * ((sqrt(189)/32 * kC3 + -9.45156237 * kS2 * kC3 + 20.47838514 * kS4 * kC3) * (kSa*(3*kCa2 - kSa2)))
  aACN54 = asig * ((3.03784720 * kS * kC2 + -22.27754615 * kS3 * kC2 + 28.96081000 * kS5 * kC2) * (2*kSa*kCa))
  aACN55 = asig * ((-sqrt(175)/32 * kC + 11.16176334 * kS2 * kC + -40.92646559 * kS4 * kC + 35.46960351 * kS6 * kC) * kSa)
  aACN56 = asig * ((-2.18750000 * kS + 19.68750000 * kS3 + -43.31250000 * kS5 + 26.81250000 * kS7))
  aACN57 = asig * ((-sqrt(175)/32 * kC + 11.16176334 * kS2 * kC + -40.92646559 * kS4 * kC + 35.46960351 * kS6 * kC) * kCa)
  aACN58 = asig * ((3.03784720 * kS * kC2 + -22.27754615 * kS3 * kC2 + 28.96081000 * kS5 * kC2) * (kCa2 - kSa2))
  aACN59 = asig * ((sqrt(189)/32 * kC3 + -9.45156237 * kS2 * kC3 + 20.47838514 * kS4 * kC3) * (kCa*(kCa2 - 3*kSa2)))
  aACN60 = asig * ((-2.84975328 * kS * kC4 + 12.34893087 * kS3 * kC4) * ((kCa2 - kSa2) ^ 2 - 4*kCa2*kSa2))
  aACN61 = asig * ((-sqrt(231)/32 * kC5 + 6.17446544 * kS2 * kC5) * (kCa*(kCa4 - 10*kCa2*kSa2 + 5*kSa4)))
  aACN62 = asig * (2.42182460 * kS * kC6 * (kCa6 - 15*kCa4*kSa2 + 15*kCa2*kSa4 - kSa6))
  aACN63 = asig * (sqrt(429)/32 * kC7 * (kCa*(kCa6 - 21*kCa4*kSa2 + 35*kCa2*kSa4 - 7*kSa6)))

  xout aACN00, aACN01, aACN02, aACN03, aACN04, aACN05, aACN06, aACN07, aACN08, aACN09, aACN10, aACN11, aACN12, aACN13, aACN14, aACN15, aACN16, aACN17, aACN18, aACN19, aACN20, aACN21, aACN22, aACN23, aACN24, aACN25, aACN26, aACN27, aACN28, aACN29, aACN30, aACN31, aACN32, aACN33, aACN34, aACN35, aACN36, aACN37, aACN38, aACN39, aACN40, aACN41, aACN42, aACN43, aACN44, aACN45, aACN46, aACN47, aACN48, aACN49, aACN50, aACN51, aACN52, aACN53, aACN54, aACN55, aACN56, aACN57, aACN58, aACN59, aACN60, aACN61, aACN62, aACN63
endop
