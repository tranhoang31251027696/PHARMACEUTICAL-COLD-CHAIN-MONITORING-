; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let (($x3219 (>= 1.0 (* alpha 1.0))))
(let ((?x2591 (ite $x3219 51 (ite $x3219 50 (ite $x3219 49 (ite $x3219 48 0))))))
(let ((?x4216 (ite (>= 13.0 (* alpha 16.0)) 64 (ite (>= 51.0 (* alpha 52.0)) 52 ?x2591))))
(let ((?x1588 (ite (>= 53.0 (* alpha 143.0)) 143 ?x4216)))
(and (distinct ?x1588 ?x1588) true))))))
(check-sat)
