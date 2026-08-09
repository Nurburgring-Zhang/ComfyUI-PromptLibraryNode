import { app } from '../../scripts/app.js'
import { api } from '../../scripts/api.js'

app.registerExtension({
    name: "PromptLibraryNode.RefImageUpload",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "PromptLibraryNodePro") return

        const origOnCreated = nodeType.prototype.onNodeCreated
        nodeType.prototype.onNodeCreated = function () {
            const r = origOnCreated?.apply(this, arguments)

            requestAnimationFrame(() => {
                const refWidget = this.widgets?.find(w => w.name === '参考图列表')
                if (!refWidget) return

                refWidget.computeSize = () => [0, -4]
                refWidget.hidden = true

                this._refImageFiles = this._refImageFiles || []
                this._refImagePreviews = this._refImagePreviews || []

                const grid = document.createElement('div')
                grid.style.cssText = 'display:grid;grid-template-columns:repeat(3,1fr);gap:6px;min-height:0;width:100%;box-sizing:border-box;'

                const syncWidget = () => {
                    refWidget.value = JSON.stringify(this._refImageFiles || [])
                    refWidget.callback?.(refWidget.value)
                }

                const calcHeight = () => {
                    const c = this._refImagePreviews?.length || 0
                    if (c === 0) return 50
                    return 50 + Math.ceil(c / 3) * 86
                }

                const redrawGrid = () => {
                    grid.innerHTML = ''
                    const files = this._refImagePreviews || []
                    if (files.length === 0) {
                        const tip = document.createElement('div')
                        tip.textContent = '点击上方按钮上传参考图（最多9张）'
                        tip.style.cssText = 'font-size:10px;opacity:0.4;padding:2px 0;'
                        grid.appendChild(tip)
                        return
                    }

                    files.forEach((imgData, idx) => {
                        const card = document.createElement('div')
                        card.style.cssText = 'position:relative;width:100%;aspect-ratio:1/1;border:1px solid var(--border-color);border-radius:4px;overflow:hidden;background:var(--comfy-input-bg);'
                        const img = document.createElement('img')
                        img.src = imgData
                        img.style.cssText = 'width:100%;height:100%;object-fit:cover;display:block;'
                        const badge = document.createElement('div')
                        badge.textContent = String(idx + 1)
                        badge.style.cssText = 'position:absolute;top:1px;left:1px;background:rgba(0,100,220,0.92);color:#fff;font-size:10px;font-weight:bold;font-family:monospace;padding:0 4px;border-radius:2px;line-height:16px;z-index:2;'
                        const del = document.createElement('div')
                        del.textContent = 'x'
                        del.style.cssText = 'position:absolute;top:1px;right:1px;width:16px;height:16px;line-height:16px;text-align:center;font-size:12px;background:rgba(200,30,30,0.85);color:#fff;border-radius:2px;cursor:pointer;z-index:3;display:none;'
                        card.onmouseenter = () => { del.style.display = 'block' }
                        card.onmouseleave = () => { del.style.display = 'none' }
                        del.onclick = (e) => {
                            e.stopPropagation()
                            this._refImageFiles.splice(idx, 1)
                            this._refImagePreviews.splice(idx, 1)
                            syncWidget(); redrawGrid()
                            app.graph.setDirtyCanvas(true)
                        }
                        card.appendChild(img)
                        card.appendChild(badge)
                        card.appendChild(del)
                        grid.appendChild(card)
                    })
                    app.graph.setDirtyCanvas(true)
                    // 直接加50px保底
                    if (this.size) {
                        this.setSize([this.size[0], this.size[1] + 60])
                    }
                }

                const fileInput = document.createElement('input')
                fileInput.type = 'file'
                fileInput.accept = 'image/png,image/jpeg,image/webp'
                fileInput.multiple = true
                fileInput.style.display = 'none'
                fileInput.onchange = async () => {
                    const newFiles = Array.from(fileInput.files || [])
                    if (newFiles.length === 0) return
                    const remaining = 9 - this._refImageFiles.length
                    const toUpload = newFiles.slice(0, remaining)
                    for (const file of toUpload) {
                        const bitmap = await createImageBitmap(file)
                        if (bitmap.width > 4096 || bitmap.height > 4096) { bitmap.close(); continue }
                        bitmap.close()
                        const reader = new FileReader()
                        await new Promise(r => { reader.onload = e => { this._refImagePreviews.push(e.target.result); r() }; reader.readAsDataURL(file) })
                        const fd = new FormData()
                        fd.append('image', file); fd.append('type', 'input'); fd.append('overwrite', 'false')
                        try {
                            const resp = await fetch('/upload/image', { method: 'POST', body: fd })
                            const result = await resp.json()
                            if (result.name || result.filename) {
                                this._refImageFiles.push({ filename: result.filename || result.name, subfolder: result.subfolder || '', type: 'input' })
                            }
                        } catch (e) { console.error('上传失败:', e) }
                        if (this._refImageFiles.length >= 9) break
                    }
                    syncWidget(); redrawGrid(); app.graph.setDirtyCanvas(true)
                    fileInput.value = ''
                }

                const restore = () => {
                    if (refWidget.value && refWidget.value !== '[]') {
                        try {
                            const files = JSON.parse(refWidget.value)
                            if (Array.isArray(files) && files.length > 0) {
                                this._refImageFiles = files
                                this._refImagePreviews = files.map(f => {
                                    const p = new URLSearchParams({ filename: f.filename, type: f.type || 'input', subfolder: f.subfolder || '' })
                                    p.append('preview', 'true')
                                    return api.apiURL('/view?' + p.toString())
                                })
                            }
                        } catch (e) {}
                    }
                }

                const headerBtn = document.createElement('button')
                headerBtn.textContent = '+ 选择文件上传'
                headerBtn.style.cssText = 'padding:4px 8px;font-size:11px;background:var(--comfy-input-bg);color:var(--input-text);border:1px solid var(--border-color);border-radius:4px;cursor:pointer;white-space:nowrap;margin-right:4px;line-height:18px;'
                headerBtn.onclick = () => fileInput.click()

                const labelSpan = document.createElement('span')
                labelSpan.textContent = '载入参考图'
                labelSpan.style.cssText = 'font-size:13px;font-weight:700;opacity:0.9;white-space:nowrap;line-height:22px;'

                const container = document.createElement('div')
                container.style.cssText = 'width:100%;display:flex;flex-direction:column;gap:8px;padding:8px;box-sizing:border-box;overflow:hidden;border:1px solid var(--border-color);border-radius:6px;background:var(--comfy-menu-bg);min-height:50px;'

                const headerRow = document.createElement('div')
                headerRow.style.cssText = 'display:flex;align-items:center;justify-content:space-between;gap:4px;width:100%;min-height:24px;'
                headerRow.appendChild(labelSpan)
                headerRow.appendChild(headerBtn)
                headerRow.appendChild(fileInput)
                container.appendChild(headerRow)
                container.appendChild(grid)

                const dw = this.addDOMWidget('ref_image_upload', 'customwidget', container, {
                    serialize: false,
                    hideOnZoom: false
                })

                dw.computeSize = function (width) {
                    return [width || 260, calcHeight()]
                }

                // 重写computeSize——累加所有widget高度，然后多加60px保底
                this.computeSize = function (width) {
                    const w = width || this.size?.[0] || 280
                    let totalH = 0
                    if (this.widgets) {
                        for (const wgt of this.widgets) {
                            if (wgt === refWidget && wgt.hidden) continue
                            if (wgt.computeSize) {
                                const sz = wgt.computeSize(w)
                                totalH += (sz?.[1] || 30)
                            } else {
                                totalH += 30
                            }
                        }
                    }
                    // 下面多给60px，让DOM widget不会超出下边框
                    return [Math.max(w, 280), totalH + 50 + 60]
                }

                const origRedraw = redrawGrid
                redrawGrid = function () {
                    origRedraw.call(this)
                    if (this.graph) this.graph.setDirtyCanvas(true)
                }

                redrawGrid()
                restore()
                setTimeout(() => { restore(); redrawGrid() }, 500)
            })
            return r
        }
    }
})
