--
-- Table structure for table `beer_log`
--

DROP TABLE IF EXISTS `beer_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `beer_log` (
  `time` datetime NOT NULL,
  `tap` int DEFAULT NULL,
  `beer_name` varchar(255) DEFAULT NULL,
  `oz_poured` float DEFAULT NULL,
  `consumer` varchar(255) DEFAULT NULL,
  `oz_remain` float DEFAULT NULL,
  `date_tapped` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `beer_log`
--

LOCK TABLES `beer_log` WRITE;
/*!40000 ALTER TABLE `beer_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `beer_log` ENABLE KEYS */;
UNLOCK TABLES;



--
-- Table structure for table `keg_log`
--

DROP TABLE IF EXISTS `keg_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `keg_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `beer_name` varchar(100) DEFAULT NULL,
  `date_tapped` varchar(100) DEFAULT NULL,
  `date_kicked` varchar(100) DEFAULT NULL,
  `days_to_consume` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `keg_log`
--

LOCK TABLES `keg_log` WRITE;
/*!40000 ALTER TABLE `keg_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `keg_log` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-09-23  3:18:19
