def get_intro_from_video(video_file):
    # if you find a intro, return intro
    # if you find a match return the longest match
    # if you find subs return the longest seq of no subs
    # else return longest pitch sequence
    return None

# identify which sequences from all sequences correlates best with the actual intro
# for each type of sequence present, identify which rules to use to pick the best one
# make a training set and a test set for all the annotated intros (70% training, 30% test)
# remove the same amount of fraction as first episodes in the set for all matching seq with intro
# make rules to reach a minimum of being able to detect intros with a margin error of 3 seconds for 95% of training set
# validate model on the testset
