; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let ((?x3876 (ite (>= 49.0 (* alpha 52.0)) 52 (ite (>= 49.0 (* alpha 51.0)) 51 0))))
(let ((?x2881 (ite (>= 25.0 (* alpha 27.0)) 54 (ite (>= 49.0 (* alpha 53.0)) 53 ?x3876))))
(let ((?x3879 (ite (>= 26.0 (* alpha 33.0)) 66 (ite (>= 10.0 (* alpha 11.0)) 55 ?x2881))))
(let ((?x2147 (ite (>= 13.0 (* alpha 17.0)) 68 (ite (>= 52.0 (* alpha 67.0)) 67 ?x3879))))
(let ((?x229 (ite (>= 53.0 (* alpha 143.0)) 143 (ite (>= 52.0 (* alpha 69.0)) 69 ?x2147))))
(and (distinct ?x229 ?x229) true)))))))
(check-sat)
