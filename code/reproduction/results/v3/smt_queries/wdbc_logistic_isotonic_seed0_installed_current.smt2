; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let (($x2089 (>= 1.0 (* alpha 1.0))))
(let ((?x1363 (ite (>= 50.0 (* alpha 51.0)) 51 (ite $x2089 50 (ite $x2089 49 (ite $x2089 48 0))))))
(let ((?x3563 (ite (>= 51.0 (* alpha 53.0)) 53 (ite (>= 25.0 (* alpha 26.0)) 52 ?x1363))))
(let ((?x894 (ite (>= 51.0 (* alpha 55.0)) 55 (ite (>= 17.0 (* alpha 18.0)) 54 ?x3563))))
(let ((?x3219 (ite (>= 17.0 (* alpha 19.0)) 57 (ite (>= 51.0 (* alpha 56.0)) 56 ?x894))))
(let ((?x4083 (ite (>= 53.0 (* alpha 75.0)) 75 (ite (>= 53.0 (* alpha 74.0)) 74 ?x3219))))
(let ((?x1586 (ite (>= 53.0 (* alpha 83.0)) 83 (ite (>= 53.0 (* alpha 82.0)) 82 ?x4083))))
(let ((?x1175 (ite (>= 53.0 (* alpha 143.0)) 143 ?x1586)))
(and (distinct ?x1175 ?x1175) true))))))))))
(check-sat)
