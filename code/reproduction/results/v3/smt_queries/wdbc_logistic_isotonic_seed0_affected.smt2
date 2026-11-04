; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let (($x2986 (>= 1.0 (* alpha 1.0))))
(let ((?x218 (ite (>= 50.0 (* alpha 51.0)) 51 (ite $x2986 50 (ite $x2986 49 (ite $x2986 48 0))))))
(let ((?x4346 (ite (>= 51.0 (* alpha 53.0)) 53 (ite (>= 25.0 (* alpha 26.0)) 52 ?x218))))
(let ((?x1496 (ite (>= 51.0 (* alpha 55.0)) 55 (ite (>= 17.0 (* alpha 18.0)) 54 ?x4346))))
(let ((?x287 (ite (>= 17.0 (* alpha 19.0)) 57 (ite (>= 51.0 (* alpha 56.0)) 56 ?x1496))))
(let ((?x1447 (ite (>= 53.0 (* alpha 74.0)) 74 ?x287)))
(let ((?x3726 (ite (>= 53.0 (* alpha 82.0)) 82 (ite (>= 53.0 (* alpha 75.0)) 75 ?x1447))))
(let ((?x3295 (ite (>= 53.0 (* alpha 143.0)) 143 (ite (>= 53.0 (* alpha 83.0)) 83 ?x3726))))
(and (distinct ?x3295 ?x1447) true))))))))))
(check-sat)
