; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let (($x716 (>= 1.0 (* alpha 1.0))))
(let ((?x593 (ite $x716 51 (ite $x716 50 (ite $x716 49 (ite $x716 48 0))))))
(let ((?x4352 (ite (>= 13.0 (* alpha 16.0)) 64 (ite (>= 51.0 (* alpha 52.0)) 52 ?x593))))
(let ((?x894 (ite (>= 53.0 (* alpha 143.0)) 143 ?x4352)))
(and (distinct ?x894 ?x894) true))))))
(check-sat)
