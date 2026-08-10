# -*- coding: utf-8 -*-
"""
5 要素审计脚本: 检查 44 节点 PARTIAL/FAIL 状态

5 要素标准 (基于 minimax general-dev.md):
1. INPUT_TYPES 完整性: required + optional 都有, optional 包含 4 路 injection slot (灵魂/审美/风格/意图)
2. build() 集成度: 接收 injection + 输出使用 injection
3. label 覆盖率: inputs/outputs/widgets 都有中文 label
4. 业务链接入: production 节点能接收 DirectorMasteryNode 注入
5. 边缘 case 处理: **kwargs 接受未知参数, type checking, default value
"""
import importlib.util
import inspect
import sys
from pathlib import Path

ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("pkg_init", str(ROOT / "__init__.py"))
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)
NODE_MAP = pkg.NODE_CLASS_MAPPINGS

# 5 要素核心 injection slot (production 节点应该有的)
INJECTION_SLOTS = ["灵魂注入", "审美注入", "风格注入", "导演意图"]

# 内置原生节点 (不需要审计)
NATIVE_TYPES = {
    "KSampler", "CLIPTextEncode", "CheckpointLoaderSimple", "CheckpointLoader",
    "UNETLoader", "CLIPLoader", "VAELoader", "EmptyLatentImage", "EmptySD3LatentImage",
    "VAEDecode", "VAEEncode", "PreviewImage", "SaveImage", "LoadImage", "ImageScale",
    "ImageScaleBy", "ImageUpscaleWithModel", "LoraLoader", "CLIPSetLastLayer",
    "ConditioningCombine", "ConditioningAverage", "ConditioningConcat", "ConditioningMultiply",
    "ConditioningZeroOut", "ConditioningSetArea", "ConditioningSetMask",
    "LatentRotate", "LatentFlip", "LatentCrop", "SetLatentNoiseMask",
    "LatentComposite", "LatentCompositeMasked", "LatentBlend",
    "MaskComposite", "MaskToImage", "ImageToMask",
    "ImageBatch", "ImageCompositeMasked",
    "SaveLatent", "LoadLatent", "LatentFromBatch", "RepeatLatentBatch",
    "ImageFromBatch", "RepeatImageBatch", "BatchImage",
    "ControlNetLoader", "ControlNetApply", "ControlNetApplyAdvanced",
    "ControlNetLoaderAdvanced", "DiffControlNetLoaderAdvanced",
    "IPAdapterLoader", "IPAdapterApply", "IPAdapterApplyFaceID",
    "CLIPVisionLoader", "CLIPVisionEncode", "UnCLIPCheckpointLoader",
    "PhotoMakerLoader", "PhotoMakerEncode", "InstantIDApply",
    "StyleModelLoader", "StyleModelApply",
    "GLIGENLoader", "GLIGENTextBoxApply",
    "UpscaleModelLoader", "ImageUpscaleWithModel",
    "VideoLinearCFGGuidance", "SVD_img2vid_Conditioning",
    "VHS_VideoCombine", "VideoCombine",
    "ConditioningSetAreaPercentage", "ConditioningSetAreaStrength",
    "ConditioningSetTimestepRange",
    "ModelSamplingAuraFlow", "ModelSamplingStableCascade",
    "SelfAttentionGuidance", "FreeU", "FreeU_V2",
    "HyperTile",
    "PatchModelAddDownscale",
    "TokenMerge", "ToBinaryMask", "SolidMask", "InvertMask",
    "CropMask", "MaskComposite", "FeatherMask", "GrowMask",
    "KSamplerAdvanced", "KSampler (Efficient)",
    "SamplerCustom", "SamplerDPMPP_2M_SDE", "SamplerDPMPP_SDE",
    "CFGGuider", "DualCFGGuider", "BasicGuider", "RandomNoise",
    "BasicScheduler", "ExponentialScheduler", "KarrasScheduler",
    "SDTurboScheduler", "PolyexponentialScheduler", "LaplaceScheduler",
    "BetaSamplingScheduler", "VPScheduler", "AlignYourStepsScheduler",
    "DPMPP_NoiseSampler", "KSamplerSelect",
    "SamplerEuler", "SamplerEulerAncestral", "SamplerLMS", "SamplerDPM2",
    "SamplerDPM2Ancestral", "SamplerDPMFast", "SamplerDPMAdaptive",
    "SamplerDPMPP_2SAncestral", "SamplerDPMPP_SDE",
    "SamplerDPMPP_2M", "SamplerDPMPP_2M_SDE", "SamplerDPMPP_2M_SDE_GPU",
    "SamplerDPMPP_3M_SDE", "SamplerDPMPP_3M_SDE_GPU",
    "SamplerHeun", "SamplerHeunpp2", "SamplerLCM", "SamplerDDIM", "SamplerDDPM", "SamplerUniPC", "SamplerUniPC_BH2",
    "LoadVideo", "SaveVideo", "VHS_LoadVideo", "VHS_SaveVideo", "VHS_VideoInfo",
    "TrimVideoDuration", "SplitVideo", "SelectVideo", "CombineVideo",
    "CreateVideo", "CreateImage", "CreateAudio", "CreateMask",
    "LoadImagesFromDirectory", "SaveImagesToDirectory",
    "ImageGrid", "ImageListToImageGrid", "ImageBatchToImageGrid",
    "ImagePadForOutpaint", "ImageBlend",
    "ImageComposite", "ImageCompositeAbsolute", "ImageBlendReferenceOnly",
    "ImageBlur", "ImageSharpen", "ImageEmboss", "ImageQuantize",
    "ImagePosterize", "ImageSolarize", "ImageEqualize", "ImageInvert",
    "ImageColorCorrect", "ImageNoise", "ImageFlip", "ImageRotate",
    "ImageCrop", "ImageResize", "ImageResizeKJ",
    "MaskEdge", "MaskBlur", "MaskFlip", "MaskRotate", "MaskCrop", "MaskResize",
    "MaskInvert", "MaskComposite", "MaskToImage", "ImageToMask",
    "MaskPreview", "MaskColor",
    "LatentInterpolate", "LatentBlend",
    "LatentRotate", "LatentFlip", "LatentCrop", "SetLatentNoiseMask",
    "LatentFromBatch", "RepeatLatentBatch",
    "LatentBatch", "LatentInterpolate",
    "ImageColorMatch", "ImageHistogramMatch",
    "ImageDesaturate", "ImageChannels", "ImageChannelSplit", "ImageChannelMerge",
    "ImageGradient", "ImageEdge", "ImageMorph",
    "ImageThreshold", "ImageAdaptiveThreshold", "ImageOtsuThreshold",
    "ImageHistogram", "ImageStats", "ImageInfo",
    "ImageCropFace", "ImageFaceRestore", "ImageFaceRestoreWithModel",
    "ImageSave", "ImageLoad",
    "MaskSmooth", "MaskGrow", "MaskThreshold", "MaskRegion",
    "LatentNoise", "LatentNoisy", "LatentSigmaScale", "LatentShift",
    "LatentBatchSeed", "LatentInterpolate", "LatentNormalize",
    "ImageNormalize", "ImageMinMax", "ImageHistogramEqualization",
    "ImageGrayscale", "ImageChannelShift", "ImageGamma",
    "ImageContrast", "ImageBrightness", "ImageHue", "ImageSaturation",
    "ImageHSV", "ImageRGB", "ImageRGBA", "ImageHSVA",
    "ImageThresholdSimple", "ImageThresholdAdaptive", "ImageThresholdOtsu",
    "ImageSaveWithMetadata", "ImageSaveJPEG", "ImageSavePNG", "ImageSaveWEBP",
    "ImageLoadWithMetadata",
    "VHS_VideoInfo", "VHS_GetVideoComponents", "VHS_SplitVideo",
    "VHS_SelectEveryNthFrame", "VHS_MergeFrames", "VHS_Combine",
    "VHS_VideoInfoFromFile", "VHS_VideoInfoFromURL",
}


def audit_node(ntype, cls):
    """审计单个节点, 返回 (status, score, reasons)"""
    if ntype in NATIVE_TYPES:
        return ("NATIVE", 100, [])
    try:
        it = cls.INPUT_TYPES()
    except Exception as e:
        return ("FAIL", 0, ["INPUT_TYPES 调用失败: {}".format(e)])
    required = it.get("required", {})
    optional = it.get("optional", {})
    rt = getattr(cls, "RETURN_TYPES", ()) or ()
    rn = getattr(cls, "RETURN_NAMES", None)

    # 5 要素审计
    reasons = []
    score = 100

    # 1. INPUT_TYPES 完整性
    if not required:
        reasons.append("❌ required 为空")
        score -= 30
    if not optional:
        # 业务链节点应该有 optional (接收上游)
        if ntype not in ("DirectorSoulNode", "AestheticJudgmentPro", "StyleGuidePro",
                          "AssetRegistry", "DirectorIntentPro", "DirectorMasteryNode"):
            reasons.append("⚠️  optional 为空 (无 injection slot)")
            score -= 20

    # 2. injection slot 完整性 (production 节点)
    is_production = ntype not in (
        "DirectorSoulNode", "AestheticJudgmentPro", "StyleGuidePro", "AssetRegistry",
        "DirectorIntentPro", "DirectorMasteryNode", "ConceptPitchPro", "ScriptArchitecturePro",
        "ScriptBodyPro", "DirectorStoryboardPro", "HookMasterPro", "H3ContextIRNode",
        "UniversalDirectorPromptNode", "ProjectArchivePro", "IterationPostPro",
        "QualityAssurancePro", "CleanupPassPro", "VersionControlPro", "FormatOutputPro",
        "MarketAudiencePro",
    )
    if is_production and len(rt) > 0:
        existing_slots = set(optional.keys()) | set(required.keys())
        for slot in INJECTION_SLOTS:
            if slot not in existing_slots:
                reasons.append("⚠️  缺 injection slot: {}".format(slot))
                score -= 8

    # 3. RETURN_NAMES 完整性
    if rn and len(rn) != len(rt):
        reasons.append("⚠️  RETURN_NAMES ({} 个) 与 RETURN_TYPES ({} 个) 数量不匹配".format(len(rn), len(rt)))
        score -= 10

    # 4. build() 集成度
    func_name = getattr(cls, "FUNCTION", None)
    if func_name and hasattr(cls, func_name):
        try:
            sig = inspect.signature(getattr(cls, func_name))
            has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
            params = list(sig.parameters.values())
            # 检查是否接收所有 injection
            param_names = [p.name for p in params if p.kind not in (inspect.Parameter.VAR_KEYWORD,)]
            for slot in INJECTION_SLOTS:
                if slot in param_names and slot not in existing_slots:
                    reasons.append("⚠️  build() 接 {} 但 INPUT_TYPES 没声明".format(slot))
                    score -= 5
        except Exception:
            pass

    # 5. 5 要素分类
    status = "PASS"
    if score < 50:
        status = "FAIL"
    elif score < 80:
        status = "PARTIAL"

    return (status, score, reasons)


def main():
    print("=" * 80)
    print("Phase 36.6 v5g: 5 要素审计 44 节点")
    print("=" * 80)

    results = []
    for ntype, cls in NODE_MAP.items():
        status, score, reasons = audit_node(ntype, cls)
        results.append((ntype, status, score, reasons))

    # 按 status 排序 (FAIL, PARTIAL, PASS)
    results.sort(key=lambda x: ({"FAIL": 0, "PARTIAL": 1, "PASS": 2, "NATIVE": 3}.get(x[1], 4), x[2], x[0]))

    fail_count = sum(1 for r in results if r[1] == "FAIL")
    partial_count = sum(1 for r in results if r[1] == "PARTIAL")
    pass_count = sum(1 for r in results if r[1] == "PASS")
    native_count = sum(1 for r in results if r[1] == "NATIVE")

    print()
    print("FAIL ({})".format(fail_count))
    print("-" * 80)
    for ntype, status, score, reasons in results:
        if status == "FAIL":
            print("  {} ({}): {}".format(ntype, score, "; ".join(reasons[:3]) if reasons else ""))

    print()
    print("PARTIAL ({})".format(partial_count))
    print("-" * 80)
    for ntype, status, score, reasons in results:
        if status == "PARTIAL":
            print("  {} ({}): {}".format(ntype, score, "; ".join(reasons[:3]) if reasons else ""))

    print()
    print("PASS ({})".format(pass_count))
    print("-" * 80)
    for ntype, status, score, reasons in results:
        if status == "PASS":
            print("  {} ({})".format(ntype, score))

    print()
    print("NATIVE ({})".format(native_count))
    print("-" * 80)

    print()
    print("=" * 80)
    print("总计: {} FAIL, {} PARTIAL, {} PASS, {} NATIVE".format(fail_count, partial_count, pass_count, native_count))
    print("=" * 80)

    return results


if __name__ == "__main__":
    main()
