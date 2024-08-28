from nk_shared.settings import ENABLE_PROFILING

if ENABLE_PROFILING:
    import cProfile  # pylint: disable=import-outside-toplevel
    import io  # pylint: disable=import-outside-toplevel
    import pstats  # pylint: disable=import-outside-toplevel

profile = None  # pylint: disable=invalid-name


def begin_profiling():
    if ENABLE_PROFILING:
        global profile  # pylint: disable=global-statement
        profile = cProfile.Profile()
        profile.enable()


def end_profiling():
    if ENABLE_PROFILING:
        profile.disable()
        s = io.StringIO()
        sortby = pstats.SortKey.TIME
        ps = pstats.Stats(profile, stream=s).sort_stats(sortby)
        ps.print_stats()
        with open("pstats.log", "w+") as f:  # pylint: disable=unspecified-encoding
            f.write(s.getvalue())
