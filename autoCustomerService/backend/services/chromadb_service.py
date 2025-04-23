
import  vannaai_service

import json

import chromadb
from openai import OpenAI
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.flask import VannaFlaskApp
from vanna.openai import OpenAI_Chat
from dotenv import load_dotenv
import os

# 加载 .env 文件中的环境变量
load_dotenv()

# 配置参数
openai_api_key = os.getenv("DEEPSEEK_API_KEY")
openai_model = os.getenv("DEEPSEEK_MODEL")
database_url = os.getenv("DATABASE_URL")
openai_base_url = os.getenv("DEEPSEEK_BASE_URL")
host_name = os.getenv("MYSQL_HOST")
user_name = os.getenv("mysql_user")
user_password = os.getenv("mysql_password")
db_name = os.getenv("MYSQL_DATABASE")
port_number = 3306
chromadb_data_path = os.getenv("CHROMA_DATA_PATH")
# 定义数据库类型（可配置）
DB_TYPE = "MySQL"  # 可选值: "MySQL", "PostgreSQL", "SQLite", "Oracle", "SQL Server"



# 初始化 OpenAI 客户端
deepseek_client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_base_url,
)

def main():
    # 实例化 MyVanna
    vn = vannaai_service.MyVanna(api_key=openai_api_key, model=openai_model, client=deepseek_client)
    # 把表的ddl信息放入向量数据库中
#     bool2 = vn.add_ddl(ddl=f"""
#     CREATE TABLE `Album`
# (
#     `AlbumId` INT NOT NULL,    `Title` NVARCHAR(160) NOT NULL,    `ArtistId` INT NOT NULL,    CONSTRAINT `PK_Album` PRIMARY KEY  (`AlbumId`));
# """)
#     print(bool2)
#     vn.add_ddl(ddl=f"""
#     CREATE TABLE `Artist`
# (
#     `ArtistId` INT NOT NULL,    `Name` NVARCHAR(120),    CONSTRAINT `PK_Artist` PRIMARY KEY  (`ArtistId`));
# """)
#
#     vn.add_ddl(ddl=f"""
#         CREATE TABLE `Customer`
# (
#     `CustomerId` INT NOT NULL,    `FirstName` NVARCHAR(40) NOT NULL,    `LastName` NVARCHAR(20) NOT NULL,    `Company` NVARCHAR(80),    `Address` NVARCHAR(70),    `City` NVARCHAR(40),    `State` NVARCHAR(40),    `Country` NVARCHAR(40),    `PostalCode` NVARCHAR(10),    `Phone` NVARCHAR(24),    `Fax` NVARCHAR(24),    `Email` NVARCHAR(60) NOT NULL,    `SupportRepId` INT,    CONSTRAINT `PK_Customer` PRIMARY KEY  (`CustomerId`));
#     """)
#
#     vn.add_ddl(ddl=f"""
#         CREATE TABLE `Employee`
# (
#     `EmployeeId` INT NOT NULL,    `LastName` NVARCHAR(20) NOT NULL,    `FirstName` NVARCHAR(20) NOT NULL,    `Title` NVARCHAR(30),    `ReportsTo` INT,    `BirthDate` DATETIME,    `HireDate` DATETIME,    `Address` NVARCHAR(70),    `City` NVARCHAR(40),    `State` NVARCHAR(40),    `Country` NVARCHAR(40),    `PostalCode` NVARCHAR(10),    `Phone` NVARCHAR(24),    `Fax` NVARCHAR(24),    `Email` NVARCHAR(60),    CONSTRAINT `PK_Employee` PRIMARY KEY  (`EmployeeId`));  """)
#
#     vn.add_ddl(ddl=f"""
#         CREATE TABLE `Genre`
# (
#     `GenreId` INT NOT NULL,    `Name` NVARCHAR(120),    CONSTRAINT `PK_Genre` PRIMARY KEY  (`GenreId`));  """)
#
#     vn.add_ddl(ddl=f"""
#         CREATE TABLE `Invoice`
# (
#     `InvoiceId` INT NOT NULL,    `CustomerId` INT NOT NULL,    `InvoiceDate` DATETIME NOT NULL,    `BillingAddress` NVARCHAR(70),    `BillingCity` NVARCHAR(40),    `BillingState` NVARCHAR(40),    `BillingCountry` NVARCHAR(40),    `BillingPostalCode` NVARCHAR(10),    `Total` NUMERIC(10,2) NOT NULL,    CONSTRAINT `PK_Invoice` PRIMARY KEY  (`InvoiceId`));  """)
#
#     vn.add_ddl(ddl=f"""
#         CREATE TABLE `InvoiceLine`
# (
#     `InvoiceLineId` INT NOT NULL,    `InvoiceId` INT NOT NULL,    `TrackId` INT NOT NULL,    `UnitPrice` NUMERIC(10,2) NOT NULL,    `Quantity` INT NOT NULL,    CONSTRAINT `PK_InvoiceLine` PRIMARY KEY  (`InvoiceLineId`));  """)
#
#     vn.add_ddl(ddl=f"""
#         CREATE TABLE `MediaType`
# (
#     `MediaTypeId` INT NOT NULL,    `Name` NVARCHAR(120),    CONSTRAINT `PK_MediaType` PRIMARY KEY  (`MediaTypeId`));  """)
#
#     vn.add_ddl(ddl=f"""
#         CREATE TABLE `Playlist`
# (
#     `PlaylistId` INT NOT NULL,    `Name` NVARCHAR(120),    CONSTRAINT `PK_Playlist` PRIMARY KEY  (`PlaylistId`));
#   """)
#
#     vn.add_ddl(ddl=f"""
#        CREATE TABLE `PlaylistTrack`
# (
#     `PlaylistId` INT NOT NULL,    `TrackId` INT NOT NULL,    CONSTRAINT `PK_PlaylistTrack` PRIMARY KEY  (`PlaylistId`, `TrackId`));   """)
#
#     vn.add_ddl(ddl=f"""
#         CREATE TABLE `Track`
# (
#     `TrackId` INT NOT NULL,    `Name` NVARCHAR(200) NOT NULL,    `AlbumId` INT,    `MediaTypeId` INT NOT NULL,    `GenreId` INT,    `Composer` NVARCHAR(220),    `Milliseconds` INT NOT NULL,    `Bytes` INT,    `UnitPrice` NUMERIC(10,2) NOT NULL,    CONSTRAINT `PK_Track` PRIMARY KEY  (`TrackId`));  """)
#
#     vn.add_ddl(ddl=f""" ALTER TABLE `Album` ADD CONSTRAINT `FK_AlbumArtistId`
#     FOREIGN KEY (`ArtistId`) REFERENCES `Artist` (`ArtistId`) ON DELETE NO ACTION ON UPDATE NO ACTION;
# CREATE INDEX `IFK_AlbumArtistId` ON `Album` (`ArtistId`);  """)
#
#     vn.add_ddl(ddl=f""" ALTER TABLE `Customer` ADD CONSTRAINT `FK_CustomerSupportRepId`
#     FOREIGN KEY (`SupportRepId`) REFERENCES `Employee` (`EmployeeId`) ON DELETE NO ACTION ON UPDATE NO ACTION;
# CREATE INDEX `IFK_CustomerSupportRepId` ON `Customer` (`SupportRepId`);  """)
#
#     vn.add_ddl(ddl=f""" ALTER TABLE `Employee` ADD CONSTRAINT `FK_EmployeeReportsTo`
#     FOREIGN KEY (`ReportsTo`) REFERENCES `Employee` (`EmployeeId`) ON DELETE NO ACTION ON UPDATE NO ACTION;
# CREATE INDEX `IFK_EmployeeReportsTo` ON `Employee` (`ReportsTo`);""")
#
#     vn.add_ddl(ddl=f""" ALTER TABLE `Invoice` ADD CONSTRAINT `FK_InvoiceCustomerId`
#     FOREIGN KEY (`CustomerId`) REFERENCES `Customer` (`CustomerId`) ON DELETE NO ACTION ON UPDATE NO ACTION;
# CREATE INDEX `IFK_InvoiceCustomerId` ON `Invoice` (`CustomerId`); """)
#
#     vn.add_ddl(ddl=f""" ALTER TABLE `InvoiceLine` ADD CONSTRAINT `FK_InvoiceLineInvoiceId`
#     FOREIGN KEY (`InvoiceId`) REFERENCES `Invoice` (`InvoiceId`) ON DELETE NO ACTION ON UPDATE NO ACTION;
# CREATE INDEX `IFK_InvoiceLineInvoiceId` ON `InvoiceLine` (`InvoiceId`);   """)
#
#     vn.add_ddl(ddl=f""" ALTER TABLE `InvoiceLine` ADD CONSTRAINT `FK_InvoiceLineTrackId`
#     FOREIGN KEY (`TrackId`) REFERENCES `Track` (`TrackId`) ON DELETE NO ACTION ON UPDATE NO ACTION;
# CREATE INDEX `IFK_InvoiceLineTrackId` ON `InvoiceLine` (`TrackId`);   """)
#
#     vn.add_ddl(ddl=f""" ALTER TABLE `PlaylistTrack` ADD CONSTRAINT `FK_PlaylistTrackPlaylistId`
#     FOREIGN KEY (`PlaylistId`) REFERENCES `Playlist` (`PlaylistId`) ON DELETE NO ACTION ON UPDATE NO ACTION;
# CREATE INDEX `IFK_PlaylistTrackPlaylistId` ON `PlaylistTrack` (`PlaylistId`);  """)
#
#     vn.add_ddl(ddl=f""" ALTER TABLE `PlaylistTrack` ADD CONSTRAINT `FK_PlaylistTrackTrackId`
#     FOREIGN KEY (`TrackId`) REFERENCES `Track` (`TrackId`) ON DELETE NO ACTION ON UPDATE NO ACTION;
# CREATE INDEX `IFK_PlaylistTrackTrackId` ON `PlaylistTrack` (`TrackId`);  """)
#
#     vn.add_ddl(ddl=f""" ALTER TABLE `Track` ADD CONSTRAINT `FK_TrackAlbumId`
#     FOREIGN KEY (`AlbumId`) REFERENCES `Album` (`AlbumId`) ON DELETE NO ACTION ON UPDATE NO ACTION;
# CREATE INDEX `IFK_TrackAlbumId` ON `Track` (`AlbumId`); """)
#
#     vn.add_ddl(ddl=f""" ALTER TABLE `Track` ADD CONSTRAINT `FK_TrackGenreId`
#     FOREIGN KEY (`GenreId`) REFERENCES `Genre` (`GenreId`) ON DELETE NO ACTION ON UPDATE NO ACTION;
# CREATE INDEX `IFK_TrackGenreId` ON `Track` (`GenreId`); """)
#
#     vn.add_ddl(ddl=f""" ALTER TABLE `Track` ADD CONSTRAINT `FK_TrackMediaTypeId`
#     FOREIGN KEY (`MediaTypeId`) REFERENCES `MediaType` (`MediaTypeId`) ON DELETE NO ACTION ON UPDATE NO ACTION;
# CREATE INDEX `IFK_TrackMediaTypeId` ON `Track` (`MediaTypeId`);""")
#



    # # 连接 MySQL 数据库
    # vn.connect_to_mysql(host=host_name, user=user_name, password=user_password, dbname=db_name, port=port_number)
    # # 测试服务
    # test_result = vn.optimize_sql_query("请给我所有的客户信息")
    # print(test_result)

    # app = VannaFlaskApp(vn, allow_llm_to_see_data=True)
    # app.run()


if __name__ == "__main__":
    main()