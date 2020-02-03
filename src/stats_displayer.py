import sys as s

import stats.intro_stats as intro_stats
import stats.matches_stats as matches_stats

if __name__ == "__main__":
    if len(s.argv) > 1:
        if s.argv[1] == "--hist-intro":
            intro_stats.plot_hist_frequency()
        elif s.argv[1] == "--intro-ss":
            intro_stats.plot_intros()
        elif s.argv[1] == "--intro-sizes":
            intro_stats.plot_hist_sizes()
        elif s.argv[1] == "--intro":
            intro_stats.plot_all_intros()
        elif s.argv[1] == "--filtering-1":
            matches_stats.plot_frequencies()
        elif s.argv[1] == "--filtering-2":
            matches_stats.plot_filtering()
        elif s.argv[1] == "--filtering-3":
            matches_stats.plot_last_sequence()
        elif s.argv[1] == "--filtering":
            matches_stats.plot_filtering()
        elif s.argv[1] == "--matches-n":
            matches_stats.plot_neighbors_frequencies()
        elif s.argv[1] == "--hash_threshold":
            matches_stats.plot_diff_threshold_hashes()
