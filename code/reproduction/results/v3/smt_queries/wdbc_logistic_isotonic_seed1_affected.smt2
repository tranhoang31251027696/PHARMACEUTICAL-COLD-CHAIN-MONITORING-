; benchmark generated from python API
(set-info :status unknown)
(declare-fun alpha () Real)
(assert
 (<= (/ 3.0 10.0) alpha))
(assert
 (>= (/ 9.0 10.0) alpha))
(assert
 (let ((?x1149 (ite (>= 49.0 (* alpha 52.0)) 52 (ite (>= 49.0 (* alpha 51.0)) 51 0))))
(let ((?x287 (ite (>= 25.0 (* alpha 27.0)) 54 (ite (>= 49.0 (* alpha 53.0)) 53 ?x1149))))
(let ((?x1584 (ite (>= 26.0 (* alpha 33.0)) 66 (ite (>= 10.0 (* alpha 11.0)) 55 ?x287))))
(let ((?x2966 (ite (>= 13.0 (* alpha 17.0)) 68 (ite (>= 52.0 (* alpha 67.0)) 67 ?x1584))))
(let ((?x4083 (ite (>= 53.0 (* alpha 143.0)) 143 (ite (>= 52.0 (* alpha 69.0)) 69 ?x2966))))
(and (distinct ?x4083 ?x4083) true)))))))
(check-sat)
