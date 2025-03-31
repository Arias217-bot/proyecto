--
-- PostgreSQL database dump
--

-- Dumped from database version 14.12
-- Dumped by pg_dump version 16.3

-- Started on 2025-03-30 11:54:09

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 3424 (class 1262 OID 74253)
-- Name: bd_volleyball_prueba; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE bd_volleyball_prueba WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'Spanish_Colombia.1252';


ALTER DATABASE bd_volleyball_prueba OWNER TO postgres;

\connect bd_volleyball_prueba

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 4 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 233 (class 1259 OID 74412)
-- Name: analisis_estadistico; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.analisis_estadistico (
    id_analisis integer NOT NULL,
    id_partido integer NOT NULL,
    informe text NOT NULL,
    grafico_url character varying(255)
);


ALTER TABLE public.analisis_estadistico OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 74411)
-- Name: analisis_estadistico_id_analisis_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.analisis_estadistico_id_analisis_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.analisis_estadistico_id_analisis_seq OWNER TO postgres;

--
-- TOC entry 3426 (class 0 OID 0)
-- Dependencies: 232
-- Name: analisis_estadistico_id_analisis_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.analisis_estadistico_id_analisis_seq OWNED BY public.analisis_estadistico.id_analisis;


--
-- TOC entry 231 (class 1259 OID 74398)
-- Name: analisis_video; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.analisis_video (
    id_analisis integer NOT NULL,
    id_partido integer NOT NULL,
    url_video character varying(255) NOT NULL,
    duracion time without time zone,
    observaciones text
);


ALTER TABLE public.analisis_video OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 74397)
-- Name: analisis_video_id_analisis_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.analisis_video_id_analisis_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.analisis_video_id_analisis_seq OWNER TO postgres;

--
-- TOC entry 3427 (class 0 OID 0)
-- Dependencies: 230
-- Name: analisis_video_id_analisis_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.analisis_video_id_analisis_seq OWNED BY public.analisis_video.id_analisis;


--
-- TOC entry 211 (class 1259 OID 74264)
-- Name: categoria_edad; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categoria_edad (
    id_categoria_edad integer NOT NULL,
    nombre character varying(50) NOT NULL
);


ALTER TABLE public.categoria_edad OWNER TO postgres;

--
-- TOC entry 210 (class 1259 OID 74263)
-- Name: categoria_edad_id_categoria_edad_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categoria_edad_id_categoria_edad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categoria_edad_id_categoria_edad_seq OWNER TO postgres;

--
-- TOC entry 3428 (class 0 OID 0)
-- Dependencies: 210
-- Name: categoria_edad_id_categoria_edad_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categoria_edad_id_categoria_edad_seq OWNED BY public.categoria_edad.id_categoria_edad;


--
-- TOC entry 213 (class 1259 OID 74271)
-- Name: categoria_sexo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categoria_sexo (
    id_categoria_sexo integer NOT NULL,
    nombre character varying(20) NOT NULL
);


ALTER TABLE public.categoria_sexo OWNER TO postgres;

--
-- TOC entry 212 (class 1259 OID 74270)
-- Name: categoria_sexo_id_categoria_sexo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categoria_sexo_id_categoria_sexo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categoria_sexo_id_categoria_sexo_seq OWNER TO postgres;

--
-- TOC entry 3429 (class 0 OID 0)
-- Dependencies: 212
-- Name: categoria_sexo_id_categoria_sexo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categoria_sexo_id_categoria_sexo_seq OWNED BY public.categoria_sexo.id_categoria_sexo;


--
-- TOC entry 229 (class 1259 OID 74386)
-- Name: detalle_jugada; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.detalle_jugada (
    id_detalle integer NOT NULL,
    id_jugada integer NOT NULL,
    jugador integer NOT NULL,
    zona integer,
    calificacion character varying(3),
    tiempo time without time zone NOT NULL,
    orden integer NOT NULL
);


ALTER TABLE public.detalle_jugada OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 74385)
-- Name: detalle_jugada_id_detalle_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.detalle_jugada_id_detalle_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.detalle_jugada_id_detalle_seq OWNER TO postgres;

--
-- TOC entry 3430 (class 0 OID 0)
-- Dependencies: 228
-- Name: detalle_jugada_id_detalle_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.detalle_jugada_id_detalle_seq OWNED BY public.detalle_jugada.id_detalle;


--
-- TOC entry 215 (class 1259 OID 74278)
-- Name: equipo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipo (
    id_equipo integer NOT NULL,
    nombre character varying(100) NOT NULL,
    id_categoria_edad integer NOT NULL,
    id_categoria_sexo integer NOT NULL,
    descripcion text
);


ALTER TABLE public.equipo OWNER TO postgres;

--
-- TOC entry 214 (class 1259 OID 74277)
-- Name: equipo_id_equipo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipo_id_equipo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.equipo_id_equipo_seq OWNER TO postgres;

--
-- TOC entry 3431 (class 0 OID 0)
-- Dependencies: 214
-- Name: equipo_id_equipo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipo_id_equipo_seq OWNED BY public.equipo.id_equipo;


--
-- TOC entry 227 (class 1259 OID 74372)
-- Name: jugadas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jugadas (
    id_jugada integer NOT NULL,
    id_partido integer NOT NULL,
    secuencia_jugada text,
    tiempo_inicio time without time zone,
    tiempo_fin time without time zone
);


ALTER TABLE public.jugadas OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 74371)
-- Name: jugadas_id_jugada_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.jugadas_id_jugada_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.jugadas_id_jugada_seq OWNER TO postgres;

--
-- TOC entry 3432 (class 0 OID 0)
-- Dependencies: 226
-- Name: jugadas_id_jugada_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.jugadas_id_jugada_seq OWNED BY public.jugadas.id_jugada;


--
-- TOC entry 225 (class 1259 OID 74361)
-- Name: jugadores_rival; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jugadores_rival (
    id_partido integer NOT NULL,
    numero integer NOT NULL,
    nombre character varying(100) NOT NULL
);


ALTER TABLE public.jugadores_rival OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 74336)
-- Name: partido; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.partido (
    id_partido integer NOT NULL,
    fecha timestamp without time zone NOT NULL,
    lugar character varying(100),
    resultado_local integer,
    resultado_rival integer,
    observaciones text
);


ALTER TABLE public.partido OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 74345)
-- Name: partido_equipo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.partido_equipo (
    id_partido_equipo integer NOT NULL,
    id_partido integer NOT NULL,
    id_equipo integer,
    nombre_rival_externo character varying(100),
    es_local boolean NOT NULL
);


ALTER TABLE public.partido_equipo OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 74344)
-- Name: partido_equipo_id_partido_equipo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.partido_equipo_id_partido_equipo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.partido_equipo_id_partido_equipo_seq OWNER TO postgres;

--
-- TOC entry 3433 (class 0 OID 0)
-- Dependencies: 223
-- Name: partido_equipo_id_partido_equipo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.partido_equipo_id_partido_equipo_seq OWNED BY public.partido_equipo.id_partido_equipo;


--
-- TOC entry 221 (class 1259 OID 74335)
-- Name: partido_id_partido_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.partido_id_partido_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.partido_id_partido_seq OWNER TO postgres;

--
-- TOC entry 3434 (class 0 OID 0)
-- Dependencies: 221
-- Name: partido_id_partido_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.partido_id_partido_seq OWNED BY public.partido.id_partido;


--
-- TOC entry 219 (class 1259 OID 74304)
-- Name: posicion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.posicion (
    id_posicion integer NOT NULL,
    nombre character varying(100) NOT NULL
);


ALTER TABLE public.posicion OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 74303)
-- Name: posicion_id_posicion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.posicion_id_posicion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.posicion_id_posicion_seq OWNER TO postgres;

--
-- TOC entry 3435 (class 0 OID 0)
-- Dependencies: 218
-- Name: posicion_id_posicion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.posicion_id_posicion_seq OWNED BY public.posicion.id_posicion;


--
-- TOC entry 217 (class 1259 OID 74297)
-- Name: rol; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rol (
    id_rol integer NOT NULL,
    nombre character varying(20) NOT NULL,
    descripcion character varying(100) NOT NULL
);


ALTER TABLE public.rol OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 74296)
-- Name: rol_id_rol_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rol_id_rol_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rol_id_rol_seq OWNER TO postgres;

--
-- TOC entry 3436 (class 0 OID 0)
-- Dependencies: 216
-- Name: rol_id_rol_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rol_id_rol_seq OWNED BY public.rol.id_rol;


--
-- TOC entry 209 (class 1259 OID 74254)
-- Name: usuario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario (
    documento character varying(20) NOT NULL,
    nombre character varying(100) NOT NULL,
    password character varying(255) NOT NULL,
    fecha_nacimiento date,
    sexo character varying(20) NOT NULL,
    telefono character varying(15),
    direccion character varying(255),
    email character varying(100),
    experiencia text,
    foto character varying(255),
);


ALTER TABLE public.usuario OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 74310)
-- Name: usuario_equipo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario_equipo (
    id_equipo integer NOT NULL,
    documento character varying(20) NOT NULL,
    id_rol integer NOT NULL,
    id_posicion integer NOT NULL
);


ALTER TABLE public.usuario_equipo OWNER TO postgres;

--
-- TOC entry 3236 (class 2604 OID 74415)
-- Name: analisis_estadistico id_analisis; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analisis_estadistico ALTER COLUMN id_analisis SET DEFAULT nextval('public.analisis_estadistico_id_analisis_seq'::regclass);


--
-- TOC entry 3235 (class 2604 OID 74401)
-- Name: analisis_video id_analisis; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analisis_video ALTER COLUMN id_analisis SET DEFAULT nextval('public.analisis_video_id_analisis_seq'::regclass);


--
-- TOC entry 3226 (class 2604 OID 74267)
-- Name: categoria_edad id_categoria_edad; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categoria_edad ALTER COLUMN id_categoria_edad SET DEFAULT nextval('public.categoria_edad_id_categoria_edad_seq'::regclass);


--
-- TOC entry 3227 (class 2604 OID 74274)
-- Name: categoria_sexo id_categoria_sexo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categoria_sexo ALTER COLUMN id_categoria_sexo SET DEFAULT nextval('public.categoria_sexo_id_categoria_sexo_seq'::regclass);


--
-- TOC entry 3234 (class 2604 OID 74389)
-- Name: detalle_jugada id_detalle; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_jugada ALTER COLUMN id_detalle SET DEFAULT nextval('public.detalle_jugada_id_detalle_seq'::regclass);


--
-- TOC entry 3228 (class 2604 OID 81920)
-- Name: equipo id_equipo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipo ALTER COLUMN id_equipo SET DEFAULT nextval('public.equipo_id_equipo_seq'::regclass);


--
-- TOC entry 3233 (class 2604 OID 74375)
-- Name: jugadas id_jugada; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jugadas ALTER COLUMN id_jugada SET DEFAULT nextval('public.jugadas_id_jugada_seq'::regclass);


--
-- TOC entry 3231 (class 2604 OID 74339)
-- Name: partido id_partido; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partido ALTER COLUMN id_partido SET DEFAULT nextval('public.partido_id_partido_seq'::regclass);


--
-- TOC entry 3232 (class 2604 OID 74348)
-- Name: partido_equipo id_partido_equipo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partido_equipo ALTER COLUMN id_partido_equipo SET DEFAULT nextval('public.partido_equipo_id_partido_equipo_seq'::regclass);


--
-- TOC entry 3230 (class 2604 OID 74307)
-- Name: posicion id_posicion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posicion ALTER COLUMN id_posicion SET DEFAULT nextval('public.posicion_id_posicion_seq'::regclass);


--
-- TOC entry 3229 (class 2604 OID 74300)
-- Name: rol id_rol; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol ALTER COLUMN id_rol SET DEFAULT nextval('public.rol_id_rol_seq'::regclass);


--
-- TOC entry 3266 (class 2606 OID 74419)
-- Name: analisis_estadistico analisis_estadistico_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analisis_estadistico
    ADD CONSTRAINT analisis_estadistico_pkey PRIMARY KEY (id_analisis);


--
-- TOC entry 3264 (class 2606 OID 74405)
-- Name: analisis_video analisis_video_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analisis_video
    ADD CONSTRAINT analisis_video_pkey PRIMARY KEY (id_analisis);


--
-- TOC entry 3242 (class 2606 OID 74269)
-- Name: categoria_edad categoria_edad_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categoria_edad
    ADD CONSTRAINT categoria_edad_pkey PRIMARY KEY (id_categoria_edad);


--
-- TOC entry 3244 (class 2606 OID 74276)
-- Name: categoria_sexo categoria_sexo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categoria_sexo
    ADD CONSTRAINT categoria_sexo_pkey PRIMARY KEY (id_categoria_sexo);


--
-- TOC entry 3262 (class 2606 OID 74391)
-- Name: detalle_jugada detalle_jugada_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_jugada
    ADD CONSTRAINT detalle_jugada_pkey PRIMARY KEY (id_detalle);


--
-- TOC entry 3246 (class 2606 OID 74285)
-- Name: equipo equipo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipo
    ADD CONSTRAINT equipo_pkey PRIMARY KEY (id_equipo);


--
-- TOC entry 3260 (class 2606 OID 74379)
-- Name: jugadas jugadas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jugadas
    ADD CONSTRAINT jugadas_pkey PRIMARY KEY (id_jugada);


--
-- TOC entry 3258 (class 2606 OID 74365)
-- Name: jugadores_rival jugadores_rival_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jugadores_rival
    ADD CONSTRAINT jugadores_rival_pkey PRIMARY KEY (id_partido, numero);


--
-- TOC entry 3256 (class 2606 OID 74350)
-- Name: partido_equipo partido_equipo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partido_equipo
    ADD CONSTRAINT partido_equipo_pkey PRIMARY KEY (id_partido_equipo);


--
-- TOC entry 3254 (class 2606 OID 74343)
-- Name: partido partido_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partido
    ADD CONSTRAINT partido_pkey PRIMARY KEY (id_partido);


--
-- TOC entry 3250 (class 2606 OID 74309)
-- Name: posicion posicion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posicion
    ADD CONSTRAINT posicion_pkey PRIMARY KEY (id_posicion);


--
-- TOC entry 3248 (class 2606 OID 74302)
-- Name: rol rol_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_pkey PRIMARY KEY (id_rol);


--
-- TOC entry 3238 (class 2606 OID 74262)
-- Name: usuario usuario_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_email_key UNIQUE (email);


--
-- TOC entry 3252 (class 2606 OID 74314)
-- Name: usuario_equipo usuario_equipo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_equipo
    ADD CONSTRAINT usuario_equipo_pkey PRIMARY KEY (id_equipo, documento, id_rol, id_posicion);


--
-- TOC entry 3240 (class 2606 OID 74260)
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (documento);


--
-- TOC entry 3279 (class 2606 OID 74420)
-- Name: analisis_estadistico analisis_estadistico_id_partido_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analisis_estadistico
    ADD CONSTRAINT analisis_estadistico_id_partido_fkey FOREIGN KEY (id_partido) REFERENCES public.partido(id_partido) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3278 (class 2606 OID 74406)
-- Name: analisis_video analisis_video_id_partido_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analisis_video
    ADD CONSTRAINT analisis_video_id_partido_fkey FOREIGN KEY (id_partido) REFERENCES public.partido(id_partido) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3277 (class 2606 OID 74392)
-- Name: detalle_jugada detalle_jugada_id_jugada_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_jugada
    ADD CONSTRAINT detalle_jugada_id_jugada_fkey FOREIGN KEY (id_jugada) REFERENCES public.jugadas(id_jugada) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3267 (class 2606 OID 74286)
-- Name: equipo equipo_id_categoria_edad_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipo
    ADD CONSTRAINT equipo_id_categoria_edad_fkey FOREIGN KEY (id_categoria_edad) REFERENCES public.categoria_edad(id_categoria_edad);


--
-- TOC entry 3268 (class 2606 OID 74291)
-- Name: equipo equipo_id_categoria_sexo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipo
    ADD CONSTRAINT equipo_id_categoria_sexo_fkey FOREIGN KEY (id_categoria_sexo) REFERENCES public.categoria_sexo(id_categoria_sexo);


--
-- TOC entry 3276 (class 2606 OID 74380)
-- Name: jugadas jugadas_id_partido_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jugadas
    ADD CONSTRAINT jugadas_id_partido_fkey FOREIGN KEY (id_partido) REFERENCES public.partido(id_partido) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3275 (class 2606 OID 74366)
-- Name: jugadores_rival jugadores_rival_id_partido_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jugadores_rival
    ADD CONSTRAINT jugadores_rival_id_partido_fkey FOREIGN KEY (id_partido) REFERENCES public.partido(id_partido) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3273 (class 2606 OID 74356)
-- Name: partido_equipo partido_equipo_id_equipo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partido_equipo
    ADD CONSTRAINT partido_equipo_id_equipo_fkey FOREIGN KEY (id_equipo) REFERENCES public.equipo(id_equipo) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- TOC entry 3274 (class 2606 OID 74351)
-- Name: partido_equipo partido_equipo_id_partido_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partido_equipo
    ADD CONSTRAINT partido_equipo_id_partido_fkey FOREIGN KEY (id_partido) REFERENCES public.partido(id_partido) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- TOC entry 3269 (class 2606 OID 74320)
-- Name: usuario_equipo usuario_equipo_documento_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_equipo
    ADD CONSTRAINT usuario_equipo_documento_fkey FOREIGN KEY (documento) REFERENCES public.usuario(documento);


--
-- TOC entry 3270 (class 2606 OID 74315)
-- Name: usuario_equipo usuario_equipo_id_equipo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_equipo
    ADD CONSTRAINT usuario_equipo_id_equipo_fkey FOREIGN KEY (id_equipo) REFERENCES public.equipo(id_equipo);


--
-- TOC entry 3271 (class 2606 OID 74330)
-- Name: usuario_equipo usuario_equipo_id_posicion_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_equipo
    ADD CONSTRAINT usuario_equipo_id_posicion_fkey FOREIGN KEY (id_posicion) REFERENCES public.posicion(id_posicion);


--
-- TOC entry 3272 (class 2606 OID 74325)
-- Name: usuario_equipo usuario_equipo_id_rol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_equipo
    ADD CONSTRAINT usuario_equipo_id_rol_fkey FOREIGN KEY (id_rol) REFERENCES public.rol(id_rol);


--
-- TOC entry 3425 (class 0 OID 0)
-- Dependencies: 4
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2025-03-30 11:54:09

--
-- PostgreSQL database dump complete
--

