-- phpMyAdmin SQL Dump
-- version 4.8.3
-- https://www.phpmyadmin.net/
--
-- Host: mysql
-- Generation Time: Jan 23, 2019 at 10:25 PM
-- Server version: 5.7.20
-- PHP Version: 7.2.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ehb2018`
--

-- --------------------------------------------------------

--
-- Table structure for table `countries`
--

CREATE TABLE `countries` (
  `id` int(11) DEFAULT NULL,
  `code` char(2) DEFAULT NULL,
  `name_en` varchar(100) DEFAULT NULL,
  `name_fr` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `countries`
--

INSERT INTO `countries` (`id`, `code`, `name_en`, `name_fr`) VALUES
(350, 'AF', 'Afghanistan', 'Afghanistan'),
(351, 'AX', 'Åland Islands', 'Îles d\'Åland'),
(352, 'AL', 'Albania', 'Albanie'),
(353, 'DZ', 'Algeria', 'Algérie'),
(354, 'AS', 'American Samoa', 'Samoa américaine'),
(355, 'AD', 'Andorra', 'Andorre'),
(356, 'AO', 'Angola', 'Angola'),
(357, 'AI', 'Anguilla', 'Anguilla'),
(358, 'AQ', 'Antarctica', 'Antarctique'),
(359, 'AG', 'Antigua and Barbuda', 'Antigua-et-Barbuda'),
(360, 'AR', 'Argentina', 'Argentine'),
(361, 'AM', 'Armenia', 'Arménie'),
(362, 'AW', 'Aruba', 'Aruba'),
(363, 'AU', 'Australia', 'Australie'),
(364, 'AT', 'Austria', 'Autriche'),
(365, 'AZ', 'Azerbaijan', 'Azerbaïdjan'),
(366, 'BS', 'Bahamas', 'Bahamas'),
(367, 'BH', 'Bahrain', 'Bahreïn'),
(368, 'BD', 'Bangladesh', 'Bangladesh'),
(369, 'BB', 'Barbados', 'Barbade'),
(370, 'BY', 'Belarus', 'Bélarus'),
(371, 'BE', 'Belgium', 'Belgique'),
(372, 'BZ', 'Belize', 'Belize'),
(373, 'BJ', 'Benin', 'Bénin'),
(374, 'BM', 'Bermuda', 'Bermudes'),
(375, 'BT', 'Bhutan', 'Bhoutan'),
(376, 'BO', 'Bolivia', 'Bolivie'),
(377, 'BA', 'Bosnia and Herzegovina', 'Bosnie-Herzégovine'),
(378, 'BW', 'Botswana', 'Botswana'),
(379, 'BV', 'Bouvet Island', 'Île Bouvet'),
(380, 'BR', 'Brazil', 'Brésil'),
(381, 'IO', 'British Indian Ocean Territory', 'Territoire britannique de l\'océan Indien'),
(382, 'BN', 'Brunei Darussalam', 'Brunei Darussalam'),
(383, 'BG', 'Bulgaria', 'Bulgarie'),
(384, 'BF', 'Burkina Faso', 'Burkina Faso'),
(385, 'BI', 'Burundi', 'Burundi'),
(386, 'KH', 'Cambodia', 'Cambodge'),
(387, 'CM', 'Cameroon', 'Cameroun'),
(388, 'CA', 'Canada', 'Canada'),
(389, 'CV', 'Cape Verde', 'Cap-Vert'),
(390, 'BQ', 'Caribbean Netherlands ', 'Pays-Bas caribéens'),
(391, 'KY', 'Cayman Islands', 'Îles Caïmans'),
(392, 'CF', 'Central African Republic', 'République centrafricaine'),
(393, 'TD', 'Chad', 'Tchad'),
(394, 'CL', 'Chile', 'Chili'),
(395, 'CN', 'China', 'Chine'),
(396, 'CX', 'Christmas Island', 'Île Christmas'),
(397, 'CC', 'Cocos (Keeling) Islands', 'Îles Cocos (Keeling)'),
(398, 'CO', 'Colombia', 'Colombie'),
(399, 'KM', 'Comoros', 'Comores'),
(400, 'CG', 'Congo', 'Congo'),
(401, 'CD', 'Congo, Democratic Republic of', 'Congo, République démocratique du'),
(402, 'CK', 'Cook Islands', 'Îles Cook'),
(403, 'CR', 'Costa Rica', 'Costa Rica'),
(404, 'CI', 'Côte d\'Ivoire', 'Côte d\'Ivoire'),
(405, 'HR', 'Croatia', 'Croatie'),
(406, 'CU', 'Cuba', 'Cuba'),
(407, 'CW', 'Curaçao', 'Curaçao'),
(408, 'CY', 'Cyprus', 'Chypre'),
(409, 'CZ', 'Czech Republic', 'République tchèque'),
(410, 'DK', 'Denmark', 'Danemark'),
(411, 'DJ', 'Djibouti', 'Djibouti'),
(412, 'DM', 'Dominica', 'Dominique'),
(413, 'DO', 'Dominican Republic', 'République dominicaine'),
(414, 'EC', 'Ecuador', 'Équateur'),
(415, 'EG', 'Egypt', 'Égypte'),
(416, 'SV', 'El Salvador', 'El Salvador'),
(417, 'GQ', 'Equatorial Guinea', 'Guinée équatoriale'),
(418, 'ER', 'Eritrea', 'Érythrée'),
(419, 'EE', 'Estonia', 'Estonie'),
(420, 'ET', 'Ethiopia', 'Éthiopie'),
(421, 'FK', 'Falkland Islands', 'Îles Malouines'),
(422, 'FO', 'Faroe Islands', 'Îles Féroé'),
(423, 'FJ', 'Fiji', 'Fidji'),
(424, 'FI', 'Finland', 'Finlande'),
(425, 'FR', 'France', 'France'),
(426, 'GF', 'French Guiana', 'Guyane française'),
(427, 'PF', 'French Polynesia', 'Polynésie française'),
(428, 'TF', 'French Southern Territories', 'Terres australes françaises'),
(429, 'GA', 'Gabon', 'Gabon'),
(430, 'GM', 'Gambia', 'Gambie'),
(431, 'GE', 'Georgia', 'Géorgie'),
(1, 'DE', 'Germany', 'Allemagne'),
(433, 'GH', 'Ghana', 'Ghana'),
(434, 'GI', 'Gibraltar', 'Gibraltar'),
(435, 'GR', 'Greece', 'Grèce'),
(436, 'GL', 'Greenland', 'Groenland'),
(437, 'GD', 'Grenada', 'Grenade'),
(438, 'GP', 'Guadeloupe', 'Guadeloupe'),
(439, 'GU', 'Guam', 'Guam'),
(440, 'GT', 'Guatemala', 'Guatemala'),
(441, 'GG', 'Guernsey', 'Guernesey'),
(442, 'GN', 'Guinea', 'Guinée'),
(443, 'GW', 'Guinea-Bissau', 'Guinée-Bissau'),
(444, 'GY', 'Guyana', 'Guyana'),
(445, 'HT', 'Haiti', 'Haïti'),
(446, 'HM', 'Heard and McDonald Islands', 'Îles Heard et McDonald'),
(447, 'HN', 'Honduras', 'Honduras'),
(448, 'HK', 'Hong Kong', 'Hong Kong'),
(449, 'HU', 'Hungary', 'Hongrie'),
(450, 'IS', 'Iceland', 'Islande'),
(451, 'IN', 'India', 'Inde'),
(452, 'ID', 'Indonesia', 'Indonésie'),
(453, 'IR', 'Iran', 'Iran'),
(454, 'IQ', 'Iraq', 'Irak'),
(455, 'IE', 'Ireland', 'Irlande'),
(456, 'IM', 'Isle of Man', 'Île de Man'),
(457, 'IL', 'Israel', 'Israël'),
(458, 'IT', 'Italy', 'Italie'),
(459, 'JM', 'Jamaica', 'Jamaïque'),
(460, 'JP', 'Japan', 'Japon'),
(461, 'JE', 'Jersey', 'Jersey'),
(462, 'JO', 'Jordan', 'Jordanie'),
(463, 'KZ', 'Kazakhstan', 'Kazakhstan'),
(464, 'KE', 'Kenya', 'Kenya'),
(465, 'KI', 'Kiribati', 'Kiribati'),
(466, 'KW', 'Kuwait', 'Koweït'),
(467, 'KG', 'Kyrgyzstan', 'Kirghizistan'),
(468, 'LA', 'Lao People\'s Democratic Republic', 'Laos'),
(469, 'LV', 'Latvia', 'Lettonie'),
(470, 'LB', 'Lebanon', 'Liban'),
(471, 'LS', 'Lesotho', 'Lesotho'),
(472, 'LR', 'Liberia', 'Libéria'),
(473, 'LY', 'Libya', 'Libye'),
(474, 'LI', 'Liechtenstein', 'Liechtenstein'),
(475, 'LT', 'Lithuania', 'Lituanie'),
(476, 'LU', 'Luxembourg', 'Luxembourg'),
(477, 'MO', 'Macau', 'Macao'),
(478, 'MK', 'Macedonia', 'Macédoine'),
(479, 'MG', 'Madagascar', 'Madagascar'),
(480, 'MW', 'Malawi', 'Malawi'),
(481, 'MY', 'Malaysia', 'Malaisie'),
(482, 'MV', 'Maldives', 'Maldives'),
(483, 'ML', 'Mali', 'Mali'),
(484, 'MT', 'Malta', 'Malte'),
(485, 'MH', 'Marshall Islands', 'Îles Marshall'),
(486, 'MQ', 'Martinique', 'Martinique'),
(487, 'MR', 'Mauritania', 'Mauritanie'),
(488, 'MU', 'Mauritius', 'Maurice'),
(489, 'YT', 'Mayotte', 'Mayotte'),
(490, 'MX', 'Mexico', 'Mexique'),
(491, 'FM', 'Micronesia, Federated States of', 'Micronésie, États fédérés de'),
(492, 'MD', 'Moldova', 'Moldavie'),
(493, 'MC', 'Monaco', 'Monaco'),
(494, 'MN', 'Mongolia', 'Mongolie'),
(495, 'ME', 'Montenegro', 'Monténégro'),
(496, 'MS', 'Montserrat', 'Montserrat'),
(497, 'MA', 'Morocco', 'Maroc'),
(498, 'MZ', 'Mozambique', 'Mozambique'),
(499, 'MM', 'Myanmar', 'Myanmar'),
(500, 'NA', 'Namibia', 'Namibie'),
(501, 'NR', 'Nauru', 'Nauru'),
(502, 'NP', 'Nepal', 'Népal'),
(2, 'NL', 'Netherlands', 'Pays-Bas'),
(504, 'NC', 'New Caledonia', 'Nouvelle-Calédonie'),
(505, 'NZ', 'New Zealand', 'Nouvelle-Zélande'),
(506, 'NI', 'Nicaragua', 'Nicaragua'),
(507, 'NE', 'Niger', 'Niger'),
(508, 'NG', 'Nigeria', 'Nigeria'),
(509, 'NU', 'Niue', 'Niue'),
(510, 'NF', 'Norfolk Island', 'Île Norfolk'),
(511, 'KP', 'North Korea', 'Corée du Nord'),
(512, 'MP', 'Northern Mariana Islands', 'Mariannes du Nord'),
(513, 'NO', 'Norway', 'Norvège'),
(514, 'OM', 'Oman', 'Oman'),
(515, 'PK', 'Pakistan', 'Pakistan'),
(516, 'PW', 'Palau', 'Palau'),
(517, 'PS', 'Palestine, State of', 'Palestine'),
(518, 'PA', 'Panama', 'Panama'),
(519, 'PG', 'Papua New Guinea', 'Papouasie-Nouvelle-Guinée'),
(520, 'PY', 'Paraguay', 'Paraguay'),
(521, 'PE', 'Peru', 'Pérou'),
(522, 'PH', 'Philippines', 'Philippines'),
(523, 'PN', 'Pitcairn', 'Pitcairn'),
(524, 'PL', 'Poland', 'Pologne'),
(525, 'PT', 'Portugal', 'Portugal'),
(526, 'PR', 'Puerto Rico', 'Puerto Rico'),
(527, 'QA', 'Qatar', 'Qatar'),
(528, 'RE', 'Réunion', 'Réunion'),
(529, 'RO', 'Romania', 'Roumanie'),
(530, 'RU', 'Russian Federation', 'Russie'),
(531, 'RW', 'Rwanda', 'Rwanda'),
(532, 'BL', 'Saint Barthélemy', 'Saint-Barthélemy'),
(533, 'SH', 'Saint Helena', 'Sainte-Hélène'),
(534, 'KN', 'Saint Kitts and Nevis', 'Saint-Kitts-et-Nevis'),
(535, 'LC', 'Saint Lucia', 'Sainte-Lucie'),
(536, 'VC', 'Saint Vincent and the Grenadines', 'Saint-Vincent-et-les-Grenadines'),
(537, 'MF', 'Saint-Martin (France)', 'Saint-Martin (France)'),
(538, 'WS', 'Samoa', 'Samoa'),
(539, 'SM', 'San Marino', 'Saint-Marin'),
(540, 'ST', 'Sao Tome and Principe', 'Sao Tomé-et-Principe'),
(541, 'SA', 'Saudi Arabia', 'Arabie saoudite'),
(542, 'SN', 'Senegal', 'Sénégal'),
(543, 'RS', 'Serbia', 'Serbie'),
(544, 'SC', 'Seychelles', 'Seychelles'),
(545, 'SL', 'Sierra Leone', 'Sierra Leone'),
(546, 'SG', 'Singapore', 'Singapour'),
(547, 'SX', 'Sint Maarten (Dutch part)', 'Saint-Martin (Pays-Bas)'),
(548, 'SK', 'Slovakia', 'Slovaquie'),
(549, 'SI', 'Slovenia', 'Slovénie'),
(550, 'SB', 'Solomon Islands', 'Îles Salomon'),
(551, 'SO', 'Somalia', 'Somalie'),
(552, 'ZA', 'South Africa', 'Afrique du Sud'),
(553, 'GS', 'South Georgia and the South Sandwich Islands', 'Géorgie du Sud et les îles Sandwich du Sud'),
(554, 'KR', 'South Korea', 'Corée du Sud'),
(555, 'SS', 'South Sudan', 'Soudan du Sud'),
(556, 'ES', 'Spain', 'Espagne'),
(557, 'LK', 'Sri Lanka', 'Sri Lanka'),
(558, 'PM', 'St. Pierre and Miquelon', 'Saint-Pierre-et-Miquelon'),
(559, 'SD', 'Sudan', 'Soudan'),
(560, 'SR', 'Suriname', 'Suriname'),
(561, 'SJ', 'Svalbard and Jan Mayen Islands', 'Svalbard et île de Jan Mayen'),
(562, 'SZ', 'Swaziland', 'Swaziland'),
(3, 'SE', 'Sweden', 'Suède'),
(564, 'CH', 'Switzerland', 'Suisse'),
(565, 'SY', 'Syria', 'Syrie'),
(566, 'TW', 'Taiwan', 'Taïwan'),
(567, 'TJ', 'Tajikistan', 'Tadjikistan'),
(568, 'TZ', 'Tanzania', 'Tanzanie'),
(569, 'TH', 'Thailand', 'Thaïlande'),
(570, 'TL', 'Timor-Leste', 'Timor-Leste'),
(571, 'TG', 'Togo', 'Togo'),
(572, 'TK', 'Tokelau', 'Tokelau'),
(573, 'TO', 'Tonga', 'Tonga'),
(574, 'TT', 'Trinidad and Tobago', 'Trinité-et-Tobago'),
(575, 'TN', 'Tunisia', 'Tunisie'),
(576, 'TR', 'Turkey', 'Turquie'),
(577, 'TM', 'Turkmenistan', 'Turkménistan'),
(578, 'TC', 'Turks and Caicos Islands', 'Îles Turks et Caicos'),
(579, 'TV', 'Tuvalu', 'Tuvalu'),
(580, 'UG', 'Uganda', 'Ouganda'),
(581, 'UA', 'Ukraine', 'Ukraine'),
(582, 'AE', 'United Arab Emirates', 'Émirats arabes unis'),
(4, 'GB', 'United Kingdom', 'Royaume-Uni'),
(584, 'UM', 'United States Minor Outlying Islands', 'Îles mineures éloignées des États-Unis'),
(5, 'US', 'United States', 'États-Unis'),
(586, 'UY', 'Uruguay', 'Uruguay'),
(587, 'UZ', 'Uzbekistan', 'Ouzbékistan'),
(588, 'VU', 'Vanuatu', 'Vanuatu'),
(589, 'VA', 'Vatican', 'Vatican'),
(590, 'VE', 'Venezuela', 'Venezuela'),
(591, 'VN', 'Vietnam', 'Vietnam'),
(592, 'VG', 'Virgin Islands (British)', 'Îles Vierges britanniques'),
(593, 'VI', 'Virgin Islands (U.S.)', 'Îles Vierges américaines'),
(594, 'WF', 'Wallis and Futuna Islands', 'Îles Wallis-et-Futuna'),
(595, 'EH', 'Western Sahara', 'Sahara Occidental'),
(596, 'YE', 'Yemen', 'Yémen'),
(597, 'ZM', 'Zambia', 'Zambie'),
(598, 'ZW', 'Zimbabwe', 'Zimbabwe');

-- --------------------------------------------------------

--
-- Table structure for table `deleted_participants`
--

CREATE TABLE `deleted_participants` (
  `id` int(11) UNSIGNED NOT NULL,
  `firstname` varchar(100) DEFAULT NULL,
  `lastname` varchar(100) DEFAULT NULL,
  `sex` varchar(10) DEFAULT NULL,
  `street` varchar(100) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `zip` varchar(20) DEFAULT NULL,
  `country` varchar(2) DEFAULT NULL,
  `final_part` smallint(1) DEFAULT NULL,
  `part1` smallint(1) DEFAULT NULL,
  `part2` smallint(1) DEFAULT NULL,
  `paypal_token` varchar(30) DEFAULT NULL,
  `last_paypal_status` smallint(1) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `exp_quartet` mediumtext,
  `exp_brigade` mediumtext,
  `exp_chorus` mediumtext,
  `exp_musical` mediumtext,
  `exp_reference` mediumtext,
  `application_time` datetime DEFAULT NULL,
  `contribution_comment` mediumtext,
  `comments` mediumtext,
  `registration_status` smallint(1) DEFAULT NULL,
  `donation` int(10) DEFAULT NULL,
  `iq_username` varchar(100) DEFAULT NULL,
  `code` varchar(16) DEFAULT NULL,
  `deletion_time` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `discounts`
--

CREATE TABLE `discounts` (
  `id` int(11) UNSIGNED NOT NULL,
  `code` varchar(8) NOT NULL,
  `amount` int(11) NOT NULL,
  `user_id` varchar(16) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `emails`
--

CREATE TABLE `emails` (
  `id` int(11) UNSIGNED NOT NULL,
  `timestamp` datetime DEFAULT NULL,
  `recipient` int(11) DEFAULT NULL,
  `subject` varchar(200) DEFAULT NULL,
  `body` text,
  `replyto` varchar(200) DEFAULT NULL,
  `sent_from` varchar(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `extras`
--

CREATE TABLE `extras` (
  `uid` int(11) UNSIGNED NOT NULL,
  `id` int(11) NOT NULL,
  `roomtype` varchar(100) NOT NULL DEFAULT '' COMMENT 'ref to "roomtypes" table',
  `roompartner` int(11) DEFAULT NULL COMMENT 'if roomtype=3, this holds participant.id ',
  `arrival_date` date NOT NULL,
  `departure_date` date NOT NULL,
  `num_show_tickets_regular` smallint(6) NOT NULL,
  `num_show_tickets_discount` smallint(6) NOT NULL,
  `t_shirt_sex` varchar(1) NOT NULL DEFAULT '' COMMENT '1=male, 2=female',
  `t_shirt_size` varchar(5) DEFAULT NULL COMMENT 'NULL=no shirt; "S", "M", etc.',
  `other` varchar(1000) NOT NULL DEFAULT '',
  `guest` varchar(1000) NOT NULL DEFAULT '',
  `num_after_concert` smallint(6) NOT NULL,
  `num_lunch_saturday` smallint(6) NOT NULL,
  `num_dinner_friday` smallint(6) NOT NULL,
  `guest1_name` varchar(200) DEFAULT NULL,
  `guest1_arrival` date DEFAULT NULL,
  `guest1_departure` date DEFAULT NULL,
  `guest1_roomtype` varchar(100) DEFAULT NULL,
  `guest2_name` varchar(200) DEFAULT NULL,
  `guest2_arrival` date DEFAULT NULL,
  `guest2_departure` date DEFAULT NULL,
  `guest2_roomtype` varchar(100) DEFAULT NULL,
  `last_paypal_status` smallint(1) DEFAULT NULL,
  `sat_night_restaurant` varchar(100) DEFAULT NULL,
  `sat_night_numpeople` smallint(6) DEFAULT NULL,
  `phone` varchar(100) DEFAULT NULL,
  `paypal_token` varchar(30) DEFAULT NULL,
  `special_event_tickets` smallint(2) DEFAULT NULL,
  `t_shirt_spec` smallint(2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `geocoding`
--

CREATE TABLE `geocoding` (
  `id` int(11) UNSIGNED NOT NULL,
  `city` varchar(100) NOT NULL DEFAULT '',
  `lat` double DEFAULT NULL,
  `long` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `guest`
--

CREATE TABLE `guest` (
  `id` int(11) UNSIGNED NOT NULL,
  `name` varchar(200) DEFAULT NULL,
  `guest_of` int(11) DEFAULT NULL,
  `guest_pos` smallint(6) DEFAULT NULL,
  `roomtype` smallint(6) DEFAULT NULL,
  `arrival` date DEFAULT NULL,
  `departure` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `guest_quartet`
--

CREATE TABLE `guest_quartet` (
  `id` int(11) UNSIGNED NOT NULL,
  `firstname` varchar(100) DEFAULT NULL,
  `lastname` varchar(100) DEFAULT NULL,
  `final_part` smallint(1) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `country` varchar(2) DEFAULT NULL,
  `iq_username` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `oops_code`
--

CREATE TABLE `oops_code` (
  `id` int(11) UNSIGNED NOT NULL,
  `code` varchar(16) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `overwritten_extras`
--

CREATE TABLE `overwritten_extras` (
  `uid` int(11) UNSIGNED NOT NULL,
  `id` int(11) NOT NULL,
  `roomtype` varchar(100) NOT NULL DEFAULT '' COMMENT 'ref to "roomtypes" table',
  `roompartner` int(11) DEFAULT NULL COMMENT 'if roomtype=3, this holds participant.id ',
  `arrival_date` date NOT NULL,
  `departure_date` date NOT NULL,
  `num_show_tickets_regular` smallint(6) NOT NULL,
  `num_show_tickets_discount` smallint(6) NOT NULL,
  `t_shirt_sex` varchar(1) NOT NULL DEFAULT '' COMMENT '1=male, 2=female',
  `t_shirt_size` varchar(5) DEFAULT NULL COMMENT 'NULL=no shirt; "S", "M", etc.',
  `other` varchar(1000) NOT NULL DEFAULT '',
  `guest` varchar(1000) NOT NULL DEFAULT '',
  `num_after_concert` smallint(6) NOT NULL,
  `num_lunch_saturday` smallint(6) NOT NULL,
  `num_dinner_friday` smallint(6) NOT NULL,
  `guest1_name` varchar(200) DEFAULT NULL,
  `guest1_arrival` date DEFAULT NULL,
  `guest1_departure` date DEFAULT NULL,
  `guest1_roomtype` varchar(100) DEFAULT NULL,
  `guest2_name` varchar(200) DEFAULT NULL,
  `guest2_arrival` date DEFAULT NULL,
  `guest2_departure` date DEFAULT NULL,
  `guest2_roomtype` varchar(100) DEFAULT NULL,
  `last_paypal_status` smallint(1) DEFAULT NULL,
  `sat_night_restaurant` varchar(100) DEFAULT NULL,
  `sat_night_numpeople` smallint(6) DEFAULT NULL,
  `phone` varchar(100) DEFAULT NULL,
  `paypal_token` varchar(30) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `special_event_tickets` smallint(2) DEFAULT NULL,
  `t_shirt_spec` smallint(2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `participant`
--

CREATE TABLE `participant` (
  `id` int(11) UNSIGNED NOT NULL,
  `firstname` varchar(100) DEFAULT NULL,
  `lastname` varchar(100) DEFAULT NULL,
  `sex` varchar(10) DEFAULT NULL,
  `street` varchar(100) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `zip` varchar(20) DEFAULT NULL,
  `country` varchar(2) DEFAULT NULL,
  `final_part` smallint(1) DEFAULT NULL,
  `part1` smallint(1) DEFAULT NULL,
  `part2` smallint(1) DEFAULT NULL,
  `paypal_token` varchar(30) DEFAULT NULL,
  `last_paypal_status` smallint(1) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `exp_quartet` mediumtext,
  `exp_brigade` mediumtext,
  `exp_chorus` mediumtext,
  `exp_musical` mediumtext,
  `exp_reference` mediumtext,
  `application_time` datetime DEFAULT NULL,
  `contribution_comment` mediumtext,
  `comments` mediumtext,
  `registration_status` smallint(1) DEFAULT NULL,
  `donation` int(10) DEFAULT NULL,
  `iq_username` varchar(100) DEFAULT NULL,
  `code` varchar(16) DEFAULT NULL,
  `member` tinyint(1) NOT NULL,
  `discounted` varchar(8) DEFAULT NULL,
  `final_fee` int(11) DEFAULT NULL,
  `confirmed` tinyint(1) NOT NULL DEFAULT '0',
  `gdpr` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `parts`
--

CREATE TABLE `parts` (
  `id` smallint(1) UNSIGNED NOT NULL,
  `name` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `parts`
--

INSERT INTO `parts` (`id`, `name`) VALUES
(1, 'Tenor'),
(2, 'Lead'),
(3, 'Baritone'),
(4, 'Bass'),
(5, 'None');

-- --------------------------------------------------------

--
-- Table structure for table `paypal_history`
--

CREATE TABLE `paypal_history` (
  `id` int(11) UNSIGNED NOT NULL,
  `participant_id` int(11) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `paypal_status` tinyint(2) DEFAULT NULL,
  `data` mediumtext,
  `payment_step` smallint(1) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `paypal_statuses`
--

CREATE TABLE `paypal_statuses` (
  `id` tinyint(2) UNSIGNED NOT NULL,
  `paypal_status_name` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `paypal_statuses`
--

INSERT INTO `paypal_statuses` (`id`, `paypal_status_name`) VALUES
(1, 'uninitialized'),
(2, 'got_token'),
(3, 'success_callback'),
(4, 'payment_approved'),
(5, 'payment_success'),
(6, 'payment_cancelled'),
(7, 'paypal_error'),
(8, 'paypal_oops');

-- --------------------------------------------------------

--
-- Table structure for table `registration_statuses`
--

CREATE TABLE `registration_statuses` (
  `id` int(11) UNSIGNED NOT NULL,
  `registration_status` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `registration_statuses`
--

INSERT INTO `registration_statuses` (`id`, `registration_status`) VALUES
(1, 'new'),
(2, 'submitted data'),
(3, 'paid deposit'),
(4, 'withdrawn'),
(5, 'withdrawn and refunded'),
(6, 'paid fully'),
(7, 'requires attention');

-- --------------------------------------------------------

--
-- Table structure for table `roomtypes`
--

CREATE TABLE `roomtypes` (
  `id` smallint(6) UNSIGNED NOT NULL,
  `description` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `room_assignments`
--

CREATE TABLE `room_assignments` (
  `uid` int(11) UNSIGNED NOT NULL,
  `name` varchar(100) NOT NULL,
  `id` int(11) UNSIGNED NOT NULL,
  `guest_position` smallint(2) DEFAULT NULL,
  `room` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `sexes`
--

CREATE TABLE `sexes` (
  `id` int(11) UNSIGNED NOT NULL,
  `name` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `sexes`
--

INSERT INTO `sexes` (`id`, `name`) VALUES
(1, 'male'),
(2, 'female');

-- --------------------------------------------------------

--
-- Table structure for table `t_shirt_specs`
--

CREATE TABLE `t_shirt_specs` (
  `id` int(11) UNSIGNED NOT NULL,
  `color` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `t_shirt_specs`
--

INSERT INTO `t_shirt_specs` (`id`, `color`) VALUES
(0, '-----'),
(1, 'apple'),
(2, 'black'),
(3, 'bottle green'),
(4, 'bright royal'),
(5, 'candy pink'),
(6, 'classic red'),
(7, 'french navy'),
(8, 'fuchsia'),
(9, 'light oxford (heather)'),
(10, 'lime'),
(11, 'orange'),
(12, 'purple'),
(13, 'sky'),
(14, 'turquoise'),
(15, 'white'),
(16, 'yellow');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) UNSIGNED NOT NULL,
  `username` varchar(100) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `deleted_participants`
--
ALTER TABLE `deleted_participants`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `paypal_token` (`paypal_token`);

--
-- Indexes for table `discounts`
--
ALTER TABLE `discounts`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `emails`
--
ALTER TABLE `emails`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `extras`
--
ALTER TABLE `extras`
  ADD PRIMARY KEY (`uid`),
  ADD KEY `id` (`id`),
  ADD KEY `paypal_token` (`paypal_token`);

--
-- Indexes for table `geocoding`
--
ALTER TABLE `geocoding`
  ADD PRIMARY KEY (`id`),
  ADD KEY `city` (`city`);

--
-- Indexes for table `guest`
--
ALTER TABLE `guest`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `guest_quartet`
--
ALTER TABLE `guest_quartet`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `oops_code`
--
ALTER TABLE `oops_code`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `code` (`code`);

--
-- Indexes for table `overwritten_extras`
--
ALTER TABLE `overwritten_extras`
  ADD PRIMARY KEY (`uid`);

--
-- Indexes for table `participant`
--
ALTER TABLE `participant`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `paypal_token` (`paypal_token`);

--
-- Indexes for table `parts`
--
ALTER TABLE `parts`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `paypal_history`
--
ALTER TABLE `paypal_history`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `paypal_statuses`
--
ALTER TABLE `paypal_statuses`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `registration_statuses`
--
ALTER TABLE `registration_statuses`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `roomtypes`
--
ALTER TABLE `roomtypes`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `room_assignments`
--
ALTER TABLE `room_assignments`
  ADD PRIMARY KEY (`uid`),
  ADD KEY `id` (`id`,`guest_position`);

--
-- Indexes for table `sexes`
--
ALTER TABLE `sexes`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `t_shirt_specs`
--
ALTER TABLE `t_shirt_specs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `deleted_participants`
--
ALTER TABLE `deleted_participants`
  MODIFY `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `discounts`
--
ALTER TABLE `discounts`
  MODIFY `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `emails`
--
ALTER TABLE `emails`
  MODIFY `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `extras`
--
ALTER TABLE `extras`
  MODIFY `uid` int(11) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `geocoding`
--
ALTER TABLE `geocoding`
  MODIFY `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `guest`
--
ALTER TABLE `guest`
  MODIFY `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `guest_quartet`
--
ALTER TABLE `guest_quartet`
  MODIFY `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `oops_code`
--
ALTER TABLE `oops_code`
  MODIFY `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `overwritten_extras`
--
ALTER TABLE `overwritten_extras`
  MODIFY `uid` int(11) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `participant`
--
ALTER TABLE `participant`
  MODIFY `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT for table `parts`
--
ALTER TABLE `parts`
  MODIFY `id` smallint(1) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `paypal_history`
--
ALTER TABLE `paypal_history`
  MODIFY `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- AUTO_INCREMENT for table `paypal_statuses`
--
ALTER TABLE `paypal_statuses`
  MODIFY `id` tinyint(2) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `registration_statuses`
--
ALTER TABLE `registration_statuses`
  MODIFY `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `roomtypes`
--
ALTER TABLE `roomtypes`
  MODIFY `id` smallint(6) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `room_assignments`
--
ALTER TABLE `room_assignments`
  MODIFY `uid` int(11) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `sexes`
--
ALTER TABLE `sexes`
  MODIFY `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `t_shirt_specs`
--
ALTER TABLE `t_shirt_specs`
  MODIFY `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) UNSIGNED NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
