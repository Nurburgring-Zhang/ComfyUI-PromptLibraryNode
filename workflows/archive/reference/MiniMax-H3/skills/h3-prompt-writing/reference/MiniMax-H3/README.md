# MiniMax-H3 Reference Pack

Source: https://github.com/MiniMax-AI/MiniMax-H3 (skills/) + https://huggingface.co/MiniMaxAI/MiniMax-H3 (docs/)

## Acquired via web_fetch (raw content delivered)
All 7 SKILL.md + 2 reference txt + 3 docs md have been delivered via web_fetch tool.
Local files are PLACEHOLDER markers pointing to the conversation context.

## 9 official SKILLs in MiniMax-H3
1. h3-prompt-writing/        - 5 prompt modes (T2VA/I2VA/FL2VA/L2VA/Ref2VA) + camera + speakers + audio
2. 3d-animation-short-generator/  - 10-step end-to-end 3D animation
3. brand-promo-video-generator/   - 10-step brand promo
4. music-video-subtitle-generator/ - MV typography + beat sync
5. minimalist-product-ad-generator/  - Apple-style product ad
6. co-op-game-intro-generator/  - co-op game menu animation
7. papercraft-stop-motion-explainer/
8. paper-collage-explainer-generator/
9. handdrawn-live-video-generator/

## Key insights to integrate into this project
1. 5 mode prompt architecture (T2VA/I2VA/FL2VA/L2VA/Ref2VA) - very similar to H3 Context IR
2. Camera motion 3D: motion type + amplitude + speed
3. Reference labels: <Subject N> / <Picture N> / <Video N> / <Audio N>
4. Speaker IDs (S1)(S2) cross-shot stable
5. <d>[Language] ...</d> dialogue format
6. <scenetrans> cross-cut dialogue / <cutoff> truncated
7. Non-diegetic music 1-3 sentences
8. overall_soundscape 1-4 sentences
9. 6-section Ref2VA: subject_definitions / summary / retention_analysis / detailed_description / overall_soundscape / non_diegetic_music
10. 3 relationship markers: fully_preserved / partially_preserved / weak_reference
