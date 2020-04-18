-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema kid_coins
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `kid_coins` ;

-- -----------------------------------------------------
-- Schema kid_coins
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `kid_coins` DEFAULT CHARACTER SET utf8 ;
USE `kid_coins` ;

-- -----------------------------------------------------
-- Table `kid_coins`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `kid_coins`.`users` ;

CREATE TABLE IF NOT EXISTS `kid_coins`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(255) NULL DEFAULT NULL,
  `last_name` VARCHAR(255) NULL DEFAULT NULL,
  `email` VARCHAR(255) NULL DEFAULT NULL,
  `password` VARCHAR(255) NULL DEFAULT NULL,
  `age` INT NULL DEFAULT NULL,
  `admin` TINYINT(1) NULL DEFAULT NULL,
  `kid` TINYINT(1) NULL DEFAULT NULL,
  `has_home` TINYINT(1) NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 36
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `kid_coins`.`homes`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `kid_coins`.`homes` ;

CREATE TABLE IF NOT EXISTS `kid_coins`.`homes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `creator_id` INT NOT NULL,
  `home_name` VARCHAR(255) NULL DEFAULT NULL,
  `home_pw` VARCHAR(255) NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_homes_users1_idx` (`creator_id` ASC) VISIBLE,
  CONSTRAINT `fk_homes_users1`
    FOREIGN KEY (`creator_id`)
    REFERENCES `kid_coins`.`users` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 19
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `kid_coins`.`family`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `kid_coins`.`family` ;

CREATE TABLE IF NOT EXISTS `kid_coins`.`family` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `home_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_homes_has_users_users1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_homes_has_users_homes1_idx` (`home_id` ASC) VISIBLE,
  CONSTRAINT `fk_homes_has_users_homes1`
    FOREIGN KEY (`home_id`)
    REFERENCES `kid_coins`.`homes` (`id`),
  CONSTRAINT `fk_homes_has_users_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `kid_coins`.`users` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 22
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `kid_coins`.`jobs`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `kid_coins`.`jobs` ;

CREATE TABLE IF NOT EXISTS `kid_coins`.`jobs` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `home_id` INT NOT NULL,
  `completed_by` INT NULL DEFAULT NULL,
  `description` VARCHAR(255) NULL DEFAULT NULL,
  `value` INT NULL DEFAULT NULL,
  `goal` TINYINT(1) NULL DEFAULT NULL,
  `task` TINYINT(1) NULL DEFAULT NULL,
  `fun` TINYINT(1) NULL DEFAULT NULL,
  `completed` TINYINT(1) NULL DEFAULT NULL,
  `approved` TINYINT(1) NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_jobs_users1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_jobs_homes1_idx` (`home_id` ASC) VISIBLE,
  CONSTRAINT `fk_jobs_homes1`
    FOREIGN KEY (`home_id`)
    REFERENCES `kid_coins`.`homes` (`id`),
  CONSTRAINT `fk_jobs_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `kid_coins`.`users` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 34
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
