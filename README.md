# Shop
yet another project

### Abstract High-level design
![c4](etc/с4.png)

### Концептуальная модель данных
![erd](etc/erd.png)

### Concrete High-level design
![concretec4](etc/concretec4.png)

### Low-level design
![lowlvl](etc/lowlvl.png)

### Логическая модель данных
![logicer](etc/logicer.png)

# ADR-001: Кэширование каталога товаров

## Status
Accepted

## Context
Интернет‑магазин Gretskie Oreshki Shop имеет большое количество операций чтения каталога товаров.

## Consequences
+ уменьшение нагрузки на PostgreSQL
+ ускорение ответа системы
- усложнение инфраструктуры

## Alternatives
Рассматривались:
- хранение только в PostgreSQL
- кеширование через Redis

## Decision
Выбран Redis, так как он снижает нагрузку на БД и ускоряет выдачу каталога.
