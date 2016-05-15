#version 330 core

/*
 * Copyright (c) 2016 David Bögelsack, Fin Christensen
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 */

in vec4 VarPosition;
in vec2 VarTexCoord;

out vec4 OutColor;

uniform sampler2D Texture;
uniform sampler2D DataTexture;
uniform int DoHarmonization;

const float PI = 3.14159265359;

float gauss (float x, float s)
{
  float m = 0.0;
  float tmp = -0.5 * (x - m) / s;
  return 1 / (sqrt (2 * PI) * s) * exp (tmp * tmp);
}

float maxValue (vec4 color)
{
  return max (color.r, max (color.g, color.b));
}

float minValue (vec4 color)
{
  return min (color.r, min (color.g, color.b));
}

vec4 rgbToHsv (vec4 color)
{
  float max_value = maxValue (color);
  float min_value = minValue (color);
  float dif = max_value - min_value;
  float add = max_value + min_value;
  vec4 outColor = vec4 (0.0, 0.0, 0.0, color.a);

  if (min_value == max_value)
    {
      outColor.r = 0.0;
    }
  else if (color.r == max_value)
    {
      outColor.r = mod (((60.0 * (color.g - color.b) / dif) + 360.0), 360.0);
    }
  else if (color.g == max_value)
    {
      outColor.r = (60.0 * (color.b - color.r) / dif) + 120.0;
    }
  else
    {
      outColor.r = (60.0 * (color.r - color.g) / dif) + 240.0;
    }

  outColor.b = 0.5 * add;

  if (outColor.b == 0.0)
    {
      outColor.g = 0.0;
    }
  else if (outColor.b <= 0.5)
    {
      outColor.g = dif / add;
    }
  else
    {
      outColor.g = dif / (2.0 - add);
    }

  outColor.r /= 360.0;

  return outColor;
}

float hueToRgb (float p, float q, float h)
{
  if (h < 0.0)
    {
      h += 1.0;
    }
  else if (h > 1.0)
    {
      h -= 1.0;
    }
  if ((h * 6.0) < 1.0)
    {
      return p + (q - p) * h * 6.0;
    }
  else if ((h * 2.0) < 1.0)
    {
      return q;
    }
  else if ((h * 3.0) < 2.0)
    {
      return p + (q - p) * ((2.0 / 3.0) - h) * 6.0;
    }
  else
    {
      return p;
    }
}

vec4 hsvToRgb (vec4 col)
{
  vec4 outColor = vec4 (0.0, 0.0, 0.0, col.a);
  float p, q, tr, tg, tb;
  if (col.b <= 0.5)
    {
      q = col.b * (1.0 + col.g);
    }
  else
    {
      q = col.b + col.g - (col.b * col.g);
    }

  p = 2.0 * col.b - q;
  tr = col.r + (1.0 / 3.0);
  tg = col.r;
  tb = col.r - (1.0 / 3.0);

  outColor.r = hueToRgb (p, q, tr);
  outColor.g = hueToRgb (p, q, tg);
  outColor.b = hueToRgb (p, q, tb);

  return outColor;
}

void main ()
{
  if (DoHarmonization != 0)
    {
      vec4 hsv_color = rgbToHsv (texture (Texture, VarTexCoord));
      vec4 data = texture (DataTexture, VarTexCoord);
      float w_over_2 = data.r / 2.0;
      hsv_color.r = data.g + w_over_2 * (1 - gauss (abs (hsv_color.r - data.g), w_over_2));
      OutColor = hsvToRgb (hsv_color);
    }
  else
    {
      OutColor = texture (Texture, VarTexCoord);
    }
}
