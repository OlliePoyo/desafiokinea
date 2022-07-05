CREATE TABLE `agenda_debentures` (
  `id` int NOT NULL AUTO_INCREMENT,
  `insert_timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `ativo` varchar(10) NOT NULL,
  `data` date NOT NULL,
  `evento` varchar(45) NOT NULL,
  `taxa` decimal(10,6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `ativo_data_evento` (`ativo`,`data`,`evento`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci