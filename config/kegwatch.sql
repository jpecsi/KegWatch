DROP TABLE IF EXISTS `beer_log`;
CREATE TABLE `beer_log` (
  `time` datetime NOT NULL,
  `tap_id` int DEFAULT NULL,
  `beer_id` varchar(100) DEFAULT NULL,
  `beer_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `consumer` varchar(255) DEFAULT NULL,
  `oz_poured` float DEFAULT NULL,
  PRIMARY KEY (`time`)
);


--
-- Table structure for table `consumers`
--
DROP TABLE IF EXISTS `consumers`;
CREATE TABLE `consumers` (
  `id` varchar(255) NOT NULL,
  `body_cat` int DEFAULT NULL,
  PRIMARY KEY (`id`)
);


--
-- Table structure for table `game_log`
--

DROP TABLE IF EXISTS `game_log`;
CREATE TABLE `game_log` (
  `game` varchar(255) NOT NULL,
  `time` datetime NOT NULL,
  `consumer` varchar(255) NOT NULL,
  `type_consumed` varchar(255) NOT NULL,
  `amount_consumed` float NOT NULL,
  `bev_abv` float DEFAULT NULL,
  `team` varchar(255) DEFAULT NULL
);

--
-- Table structure for table `games`
--

DROP TABLE IF EXISTS `games`;
CREATE TABLE `games` (
  `id` varchar(255) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `date` varchar(255) DEFAULT NULL,
  `players` int DEFAULT NULL,
  `status` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);


--
-- Table structure for table `keg_log`
--
DROP TABLE IF EXISTS `keg_log`;
CREATE TABLE `keg_log` (
  `id` varchar(255) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `tap` int DEFAULT NULL,
  `abv` float DEFAULT NULL,
  `capacity` float DEFAULT NULL,
  `remaining` float DEFAULT NULL,
  `date_tapped` varchar(100) DEFAULT NULL,
  `date_kicked` varchar(100) DEFAULT NULL,
  `days_to_consume` int DEFAULT NULL,
  `status` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`id`)
);

--
-- Table structure for table `teams`
--

DROP TABLE IF EXISTS `teams`;
CREATE TABLE `teams` (
  `game` varchar(255) NOT NULL,
  `consumer` varchar(255) NOT NULL,
  `team` varchar(255) NOT NULL
);
