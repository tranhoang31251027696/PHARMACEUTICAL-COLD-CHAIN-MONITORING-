; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let ((?x92 (ite (>= 50.0 (* alpha 51.0)) 51 (ite (>= 1.0 (* alpha 1.0)) 50 0))))
(let ((?x1959 (ite (>= 52.0 (* alpha 53.0)) 53 (ite (>= 51.0 (* alpha 52.0)) 52 ?x92))))
(let ((?x2966 (ite (>= 53.0 (* alpha 56.0)) 56 (ite (>= 52.0 (* alpha 55.0)) 55 ?x1959))))
(let ((?x3972 (ite (>= 53.0 (* alpha 143.0)) 143 ?x2966)))
(and (distinct ?x3972 ?x3972) true))))))
(check-sat)
