; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let ((?x3876 (ite (>= 13.0 (* alpha 18.0)) 72 (ite (>= 51.0 (* alpha 53.0)) 53 0))))
(let ((?x2964 (ite (>= 26.0 (* alpha 37.0)) 74 (ite (>= 52.0 (* alpha 73.0)) 73 ?x3876))))
(let ((?x2314 (ite (>= 53.0 (* alpha 143.0)) 143 ?x2964)))
(and (distinct ?x2314 ?x2314) true)))))
(check-sat)
