; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let (($x503 (>= 1.0 (* alpha 1.0))))
(let ((?x1189 (ite (>= 53.0 (* alpha 55.0)) 55 (ite $x503 50 (ite $x503 49 (ite $x503 48 0))))))
(let ((?x542 (ite (>= 53.0 (* alpha 79.0)) 79 (ite (>= 53.0 (* alpha 57.0)) 57 ?x1189))))
(let ((?x1175 (ite (>= 53.0 (* alpha 81.0)) 81 (ite (>= 53.0 (* alpha 80.0)) 80 ?x542))))
(let ((?x389 (ite (>= 53.0 (* alpha 83.0)) 83 (ite (>= 53.0 (* alpha 82.0)) 82 ?x1175))))
(let ((?x3726 (ite (>= 53.0 (* alpha 143.0)) 143 (ite (>= 53.0 (* alpha 84.0)) 84 ?x389))))
(and (distinct ?x3726 ?x1189) true))))))))
(check-sat)
