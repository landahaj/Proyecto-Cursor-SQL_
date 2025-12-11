CREATE DATABASE JuegoBatallas;
GO

USE JuegoBatallas;
GO

CREATE TABLE Batallas (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Jugador NVARCHAR(50),
    Enemigo NVARCHAR(50),
    DañoTotal INT,
    Ganador NVARCHAR(20),
    Fecha DATETIME DEFAULT GETDATE()
);

SELECT * FROM Batallas;
