from .db import (  # noqa
    test_init,
    test_load_redis,

    test_link_exist_redis,
    test_get_link_properties_redis,

    test_no_result_redis,
    test_one_result_redis,
    test_all_results_redis,

    test_addlink_redis,
    test_deletelink_redis,
    test_updatelink_redis,

    test_sorted_links_redis
)

from .interface import (  # noqa
    test_cmd_flush,

    test_cmd_addlinks,
    test_cmd_addlinks_with_update,
    test_cmd_addlinks_dump,

    test_cmd_updatelinks,
    test_cmd_updatelinks_with_add,
    test_cmd_updatelinks_dump,

    test_cmd_removelinks,
    test_cmd_removelinks_dump,

    test_cmd_load_null,
    test_cmd_one_load,
    test_cmd_dump_after_one_load,
    test_cmd_multi_load,
    test_cmd_dump_after_multi_load,

    test_cmd_searchlinks_allresult,
    test_cmd_searchlinks_noresult,
    test_cmd_searchlinks
)
