#include <stdio.h>
#include <stdint.h>

#define MAX_ENTRIES 1024
#define HIST_BINS 10

extern uint64_t timestamps[MAX_ENTRIES];
extern int timestampIndex;

void computeHistogram() {
    if (timestampIndex < 2) {
        printf("Not enough samples for histogram.\n");
        return;
    }

    uint64_t min_delta = UINT64_MAX, max_delta = 0;
    uint64_t deltas[MAX_ENTRIES - 1];
    uint64_t l_bindices[HIST_BINS] = {0}; // Lower bin indices
    uint64_t u_bindices[HIST_BINS] = {0}; // Upper bin indices

    // Compute time differences
    for (int i = 1; i < timestampIndex; i++) {
        deltas[i - 1] = timestamps[i] - timestamps[i - 1];
        if (deltas[i - 1] < min_delta) min_delta = deltas[i - 1];
        if (deltas[i - 1] > max_delta) max_delta = deltas[i - 1];
    }

    // Compute histogram bins
    uint64_t bin_size = (max_delta - min_delta) / HIST_BINS;
    int histogram[HIST_BINS] = {0};

    for (int i = 0; i < HIST_BINS; i++) {
        l_bindices[i] = min_delta + i * bin_size;
        u_bindices[i] = (i == HIST_BINS - 1) ? max_delta : l_bindices[i] + bin_size;
    }

    for (int i = 0; i < timestampIndex - 1; i++) {
        int bin = (deltas[i] - min_delta) / bin_size;
        if (bin >= HIST_BINS) bin = HIST_BINS - 1;
        histogram[bin]++;
    }

    // Print histogram
    printf("Histogram of rdtsc() time differences:\n");
    for (int i = 0; i < HIST_BINS; i++) {
        // printf("[%d - %d] Cycles: %d\n", i, histogram[i]);
        printf("[%lu - %lu] Cycles: %d\n", l_bindices[i], u_bindices[i], histogram[i]);
    }
}
