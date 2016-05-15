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

layout (location = 0) in vec2 InPosition;
layout (location = 1) in vec2 InTexCoord;

uniform mat4 ProjectionMatrix;
uniform mat4 WorldMatrix;

out vec4 VarPosition;
out vec2 VarTexCoord;
out vec2 VarSectorProperties;

void main ()
{
  VarPosition = ProjectionMatrix * WorldMatrix * vec4 (InPosition, 0.0, 1.0);
  VarTexCoord = InTexCoord;
  gl_Position = VarPosition;
}
