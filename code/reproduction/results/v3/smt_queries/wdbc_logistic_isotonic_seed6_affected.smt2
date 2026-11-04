; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let ((?x1175 (ite (>= 13.0 (* alpha 18.0)) 72 (ite (>= 51.0 (* alpha 53.0)) 53 0))))
(let ((?x4216 (ite (>= 26.0 (* alpha 37.0)) 74 (ite (>= 52.0 (* alpha 73.0)) 73 ?x1175))))
(let ((?x1959 (ite (>= 53.0 (* alpha 143.0)) 143 ?x4216)))
(and (distinct ?x1959 ?x1959) true)))))
(check-sat)
