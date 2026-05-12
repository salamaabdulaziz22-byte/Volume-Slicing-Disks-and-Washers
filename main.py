## Goal

Express the radius the way it's actually computed in class:

- **Axis horizontal** (`y = k`) → radius is **vertical**, so the radius is a difference of **y-values** (top y − bottom y).
- **Axis vertical** (`x = h`) → radius is **horizontal**, so the radius is a difference of **x-values** (right x − left x).

Apply this to both Step 5 (find the radius) and Step 6 (substitute into the formula), for Disk and Washer cases.

## Where this lives

`src/lib/volume.ts`, in `solveVolume`. Steps 5 and 6 currently render the radius as `|f(t) − axisValue|`. We'll switch to the "top − bottom" / "right − left" form, picking the correct top/bottom (or right/left) curve at the midpoint of `[a, b]`.

## Conventions

Let `u` be the dependent direction (perpendicular to the integration variable):

- `tVar = x`, `axisVar = y` → `u = y`. "Top" = larger y, "Bottom" = smaller y. Radius is in y.
- `tVar = y`, `axisVar = x` → `u = x`. "Right" = larger x, "Left" = smaller x. Radius is in x.

At the midpoint `tMid = (a+b)/2`, gather `u`-values from each non-tLine boundary using existing `valuesAt`. Add the axis itself (`axisValue`) as a virtual candidate when classifying which side of the region the axis sits on.

### Disk (region's near edge is the axis)

The radius spans from the axis to the far edge of the region.

- Horizontal axis: `R(x) = topCurve(x) − k` if the region is above the axis, or `R(x) = k − bottomCurve(x)` if below. Equivalently: `R = top − bottom` where one of {top, bottom} is the axis.
- Vertical axis: `R(y) = rightCurve(y) − h` or `h − leftCurve(y)`.

Step 5 text (Disk, axis horizontal):
```
Radius is vertical (axis is horizontal y = k), so R = (top y) − (bottom y).
Top:    y = <farCurve.label or "k">
Bottom: y = <nearCurve.label or "k">
R(x) = <farExpr> − <nearExpr>
```

Vertical axis variant swaps wording to "right x − left x".

### Washer (gap between region and axis)

Both edges of the region are away from the axis.

- Horizontal axis: `R(x) = topCurve(x) − k`, `r(x) = bottomCurve(x) − k` (when region is fully above axis). Mirror when fully below.
- Vertical axis: `R(y) = rightCurve(y) − h`, `r(y) = leftCurve(y) − h`.

Step 5 text (Washer, axis horizontal):
```
Radius is vertical (axis is horizontal y = k), so each radius = (a y-value) − (axis y).
Outer R(x) = (farther y) − k = <farCurve> − <k>
Inner r(x) = (closer y) − k = <nearCurve> − <k>
```

Vertical axis variant uses "(an x-value) − h" with right/left.

### Step 6 substitution

Render the integrand using the symbolic `R` and `r` strings built in Step 5 (don't re-derive). Examples:

- Disk: `V = π ∫ₐᵇ ( <farExpr> − <nearExpr> )² dt`
- Washer: `V = π ∫ₐᵇ ( (<topExpr> − k)² − (<bottomExpr> − k)² ) dt`

## Implementation outline

In `solveVolume`, after `tMid` / `scored` are computed:

1. Build `uAt(p)` returning the representative `u`-value of boundary `p` at `tMid` (use the closest-to-axis or first sample from `valuesAt`; for `uConst` it's `p.u`).
2. Determine `aboveAxis` = whether the region's u-values sit above or below `axisValue` at `tMid` (sign of `medianU − axisValue`). For washer this picks orientation; for disk it determines which side is the axis.
3. Pick `farCurve` (max `|u − axis|`) and `nearCurve` (min `|u − axis|`) at `tMid`. For disk, the near edge is the axis itself, so render the near term as `axisValue` rather than a curve.
4. Helper `exprFor(p)` returns the raw RHS of a `direct` boundary (`label.split("=")[1]`) or the constant for `uConst`. Skip any boundary whose dependent variable doesn't match `axisVar` (we can't write its u-value as a simple expression in t; fall back to the existing `R(t)`/`r(t)` placeholder in that case).
5. Build symbolic strings:
   - `Rsym = "(" + farExpr + ") − (" + axisValue + ")"` (or flipped if region below axis), simplifying when `axisValue === 0` to just `(farExpr)`.
   - `rsym` similarly for washer.
   - For disk, `Rsym = "(" + topExpr + ") − (" + bottomExpr + ")"` where one of those is the axis value.
6. Use `Rsym`/`rsym` in Step 5 body and Step 6 body.

## Out of scope

- No change to numerical integration (`Rfun`, `rfun`, `simpson`) — this is a presentation/derivation change.
- No change to `parseBoundary`, `makeTraces`, or `FunctionPlot`.
- Disk-vs-washer detection logic stays as-is for this change.
