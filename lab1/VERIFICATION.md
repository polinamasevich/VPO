# Верификация требований

Проверка выполнена на работающем Django-приложении через Django test client: реальные маршруты, middleware, формы, ORM, шаблоны и отдельная SQLite-БД. Это серверная функциональная проверка без настоящего браузера; визуальная адаптивность и реальный production deployment здесь не проверялись. Unit-тесты отдельно изолируют зависимости.

Воспроизведение: `python lab2/run_tests.py`. Полные имена выполненных тестов и результаты — `lab2/reports/test-output.txt`. Четыре проверки ожидаемого контракта имеют expectedFailure: это воспроизведённые открытые дефекты, а не успешно выполненные требования.

## Проверка формулировок

| Непроверяемая исходная идея | Измеримая формулировка |
|---|---|
| «Удобный выбор» | BR-01: каталог, фильтр, сортировка и карточка доступны посетителю |
| «Безопасная авторизация» | NFR-01: хеш вместо открытого пароля; FR-15: неверный пароль отклонён |
| «Надёжное оформление» | FR-11/12: ошибки сохраняют корзину, успех её очищает |
| «Качественные тесты» | NFR-05: coverage.py измеряет ≥70% строк в указанной области |

Все требования ниже имеют критерий и метод проверки; непроверяемых формулировок в спецификации не оставлено.

## Матрица всех требований

Имена `test_*` ищутся в `lab2/tests/`; метод проверки — автоматизированный тест указанного поведения, кроме NFR-05 (измерение coverage.py).

| ID | Способ проверки / доказательство | Результат |
|---|---|---|
| BR-01 | test_catalog_filters_category; test_catalog_sort_orders; test_product_detail_and_missing_product | Подтверждено |
| BR-02 | test_active_promo_calculates_discount_case_insensitively; test_checkout_error_corrected_then_success | Подтверждено в пределах демонстрационного оформления |
| BR-03 | test_review_created_edited_deleted_by_owner; test_stranger_cannot_change_published_review | Подтверждено для авторизованных пользователей |
| UR-01 | test_catalog_filters_category; test_catalog_sort_orders; test_product_detail_and_missing_product | Подтверждено |
| UR-02 | test_information_pages_display_database_content; test_static_and_auth_pages_render | Подтверждено |
| UR-03 | test_registration_persists_user_and_creates_session; test_registration_age_boundary_with_mocked_clock; test_login_success_failure_and_logout | Подтверждено |
| UR-04 | test_cart_quantity_transitions | Подтверждено |
| UR-05 | test_checkout_delivery_and_pickup; test_checkout_error_corrected_then_success; test_active_promo_calculates_discount_case_insensitively | Подтверждено |
| UR-06 | test_review_created_edited_deleted_by_owner | Подтверждено |
| UR-07 | test_admin_creates_category; test_statistics_with_no_products; test_statistics_for_products_without_categories; test_D02_stats_with_category_must_render | Частично: D-02 |
| FR-01 | test_catalog_filters_category | Подтверждено |
| FR-02 | test_catalog_sort_orders | Подтверждено |
| FR-03 | test_product_detail_and_missing_product | Подтверждено |
| FR-04 | test_cart_quantity_transitions; test_get_cannot_add_to_cart | Подтверждено |
| FR-05 | test_cart_total_from_database_and_sessions_are_isolated; test_cart_total_filters_corrupted_session_with_mocked_database | Подтверждено |
| FR-06 | test_cart_quantity_transitions | Подтверждено |
| FR-07 | test_empty_checkout_redirect; test_checkout_error_corrected_then_success | Подтверждено |
| FR-08 | test_checkout_invalid_fields | Подтверждено |
| FR-09 | test_checkout_delivery_and_pickup | Подтверждено |
| FR-10 | test_active_promo_calculates_discount_case_insensitively | Подтверждено |
| FR-11 | test_invalid_promos_preserve_cart | Подтверждено |
| FR-12 | test_checkout_error_corrected_then_success | Подтверждено |
| FR-13 | test_registration_phone_format; test_registration_age_boundary_with_mocked_clock | Подтверждено |
| FR-14 | test_registration_persists_user_and_creates_session; test_registration_rejects_duplicate_username | Подтверждено |
| FR-15 | test_login_success_failure_and_logout | Подтверждено |
| FR-16 | test_review_rating_boundaries; test_review_text_boundary | Подтверждено |
| FR-17 | test_review_created_edited_deleted_by_owner | Подтверждено |
| FR-18 | test_stranger_cannot_change_published_review; test_staff_can_edit_and_delete_another_users_review | Подтверждено |
| FR-19 | test_invalid_create_and_edit_do_not_change_state; test_edited_review_repeated_updates_and_rejections | Подтверждено |
| FR-20 | test_D04_get_must_not_delete_review | Не выполнено: D-04 |
| FR-21 | test_news_limit_and_order | Подтверждено |
| FR-22 | test_information_pages_display_database_content | Подтверждено |
| FR-23 | test_statistics_guest_and_regular_user_cannot_access; test_statistics_for_products_without_categories; test_D02_stats_with_category_must_render | Частично: D-02 |
| FR-24 | test_D01_anonymous_review_post_must_not_return_500 | Не выполнено: D-01 |
| FR-25 | test_D03_invalid_category_must_not_return_500 | Не выполнено: D-03 |
| FR-26 | test_admin_creates_category | Подтверждено |
| NFR-01 | test_password_hash_and_commit_behavior_with_mocked_repository; test_registration_persists_user_and_creates_session | Подтверждено; в тестовых настройках ускоренный хешер |
| NFR-02 | test_csrf_rejects_post_without_token | Подтверждено |
| NFR-03 | test_cart_total_from_database_and_sessions_are_isolated | Подтверждено |
| NFR-04 | test_D01_anonymous_review_post_must_not_return_500; test_D03_invalid_category_must_not_return_500 | Не выполнено: D-01, D-03 |
| NFR-05 | python lab2/run_tests.py; lab2/reports/coverage.txt | См. измеренный результат в отчёте |
| NFR-06 | test_information_pages_display_database_content; test_review_created_edited_deleted_by_owner | Подтверждено |
| EXT-01 | test_partner_http_statuses; test_transport_failure_and_timeout; test_invalid_scheme_makes_no_http_request | Подтверждено для отдельного дополнения lab2, не для страниц сайта |

Дефекты и точные шаги воспроизведения: [ISSUES.md](ISSUES.md). Утверждение «подтверждено» относится к проверенным наборам данных, а не ко всем возможным входам.
